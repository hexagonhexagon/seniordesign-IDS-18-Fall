import QtQuick 2.12
import QtQuick.Window 2.12
import QtQuick.Controls 2.5
import QtQuick.Dialogs 1.3

ApplicationWindow {
    id: root
    visible: true
    title: qsTr("Two Stage IDS Tester")
    width: 640
    height: 480

    Column {
        x: 10
        y: 10
        spacing: 20
        // GroupBox creates a frame around the following things.
        GroupBox {
            title: "Create ID Probs"
            Column {
                anchors.fill: parent
                spacing: 5

                // Allow the user to select multiple files to turn into an ID
                // probabilities file. Must specify the title of the dialog that
                // comes up as well as the filter (name of filter, then actual
                // filter in parentheses). Definition in MultiFileSelect.qml.
                MultiFileSelect {
                    id: idprobsFileSelect
                    title: qsTr("Select files for ID probabilities file")
                    nameFilters: "CAN Frame Files (*.json *.traffic *.csv)"
                }

                // Allow the user to specify the new name of the ID probabilities file.
                Row {
                    spacing: 5
                    Label {
                        text: "ID Probs Name"
                        height: idprobsName.height
                        verticalAlignment: Text.AlignVCenter
                    }
                    TextField {
                        id: idprobsName
                    }
                }

                // Actually use the Data Preprocessor Manager (Already set up
                // dpManager to correspond to the actual object in the entry point)
                // to create the ID probabilities file. MultiFileSelect.fileUrls
                // contains the list of files that the user picked. This is
                // blocking at the moment, working on making it non-blocking.
                Button {
                    id: makeIdprobsButton
                    text: qsTr("Make ID Probs File")
                    onClicked: dpManager.create_idprobs_file(idprobsFileSelect.fileUrls, idprobsName.text)
                }
            }
        }

        GroupBox {
            title: "Create Dataset"
            Column {
                anchors.fill: parent
                spacing: 5

                // Allow the user to specify a single file. Same as
                // MultiFileSelect, except the file selected is in
                // SingleFileSelect.fileUrl. Defined in SingleFileSelect.qml.
                SingleFileSelect {
                    id: datasetFileSelect
                    title: qsTr("Select file to make dataset")
                    nameFilters: "CAN Frame Files (*.json *.traffic *.csv)"
                }

                // Specify the ID probabilties file to use using a dropdown box
                // (ComboBox). The availableIdprobs property of the Data
                // Preprocessor Manager is set up to be a list of all ID probs
                // files that the manager can find in the savedata folder.
                Row {
                    spacing: 5
                    Label {
                        text: qsTr("ID Probs to Use")
                    }

                    ComboBox {
                        id: datasetIdprobs
                        model: dpManager.availableIdprobs
                    }
                }

                // Specify the name of the dataset to use.
                Row {
                    spacing: 5
                    Label {
                        text: "Dataset Name"
                        height: datasetName.height
                        verticalAlignment: Text.AlignVCenter
                    }
                    TextField {
                        id: datasetName
                    }
                }

                // Allow the Malicious Packet Generator injection probabilities
                // to be specified.
                Column {
                    Label {
                        text: qsTr("Attack Injection Probabilities")
                    }

                    // MaliciousGeneratorSlider is a label, with a slider from
                    // 0.0-1.0, and a text box that displays the current value and
                    // can be changed to change the value of the slider.
                    MaliciousGeneratorSlider {
                        id: noAttackSlider
                        label: qsTr("No Attack")
                        value: 0.5
                        // If the no attack slider is moved, proportionally
                        // scale up or down all other attacks to ensure the
                        // probabilities sum to 1.
                        onMoved: {
                            // Get (1 - previous slider value).
                            var attackValueSum =  randomSlider.value +
                            floodSlider.value + replaySlider.value +
                            spoofSlider.value
                            if (attackValueSum == 0.0) {
                                // If sum was 0, scale up other slider values equally.
                                var newValue = (1 - value) / 4
                                randomSlider.value = newValue
                                floodSlider.value = newValue
                                replaySlider.value = newValue
                                spoofSlider.value = newValue
                            }
                            else {
                                // Otherwise, scale up other slider values by
                                // multiplying by (1 - new value) / (1 - old
                                // value), which ensures everything sums to 1.
                                var multiplier = (1 - value) / attackValueSum
                                randomSlider.value *= multiplier
                                floodSlider.value *= multiplier
                                replaySlider.value *= multiplier
                                spoofSlider.value *= multiplier
                            }
                        }
                    }
                    MaliciousGeneratorSlider {
                        id: randomSlider
                        label: qsTr("Random Attack")
                        value: 0.125
                        // If a non-no attack slider is moved, adjust the
                        // No Attack slider up or down relative to the new value of
                        // this slider. If No Attack is brought to 0, this slider
                        // cannot be moved any further to the right. The code is
                        // very similar for the 3 sliders after this one.
                        onMoved: {
                            // Find the sum of all the other attacks.
                            var otherValueSum =  floodSlider.value + replaySlider.value + spoofSlider.value
                            if (value + otherValueSum <= 1.0)  {
                                // Is the new sum of the attack probabilities
                                // less than 1? If so, we adjust the No Attack
                                // slider accordingly.
                                noAttackSlider.value = 1 - value - otherValueSum
                            }
                            else {
                                // Otherwise, No Attack is at 0 and we set this
                                // slider value to the highest it can be without
                                // getting the probabilities to sum greater than
                                // 1.
                                noAttackSlider.value = 0.0
                                value = 1 - otherValueSum
                            }
                        }
                    }
                    MaliciousGeneratorSlider {
                        id: floodSlider
                        label: qsTr("Flood Attack")
                        value: 0.125
                        onMoved: {
                            var otherValueSum =  randomSlider.value + replaySlider.value + spoofSlider.value
                            if (value + otherValueSum <= 1.0)  {
                                noAttackSlider.value = 1 - value - otherValueSum
                            }
                            else {
                                noAttackSlider.value = 0.0
                                value = 1 - otherValueSum
                            }
                        }
                    }
                    MaliciousGeneratorSlider {
                        id: replaySlider
                        label: qsTr("Replay Attack")
                        value: 0.125
                        onMoved: {
                            var otherValueSum =  randomSlider.value + floodSlider.value + spoofSlider.value
                            if (value + otherValueSum <= 1.0)  {
                                noAttackSlider.value = 1 - value - otherValueSum
                            }
                            else {
                                noAttackSlider.value = 0.0
                                value = 1 - otherValueSum
                            }
                        }
                    }
                    MaliciousGeneratorSlider {
                        id: spoofSlider
                        label: qsTr("Spoofing Attack")
                        value: 0.125
                        onMoved: {
                            var otherValueSum =  randomSlider.value + floodSlider.value + replaySlider.value
                            if (value + otherValueSum <= 1.0)  {
                                noAttackSlider.value = 1 - value - otherValueSum
                            }
                            else {
                                noAttackSlider.value = 0.0
                                value = 1 - otherValueSum
                            }
                        }
                    }
                }

                // Generate the dataset.
                Button {
                    id: makeDatasetButton
                    text: qsTr("Make Dataset")
                    onClicked: {
                        // We set up the adjustment dictionary to pass in to the
                        // create_dataset function to be the probabilities we
                        // just specified as a JS object.
                        var malgenSettings = {
                            "none": noAttackSlider.value,
                            "random": randomSlider.value,
                            "flood": floodSlider.value,
                            "replay": replaySlider.value,
                            "spoof": spoofSlider.value
                        }
                        // Call the function. We get the file selected via
                        // SingleFileSelect.fileUrl, and we pass in the
                        // adjustments we just specified.
                        dpManager.create_dataset(datasetFileSelect.fileUrl, datasetIdprobs.currentText, malgenSettings, datasetName.text)
                    }
                }
            }
        }
    }
}
