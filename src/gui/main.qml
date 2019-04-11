import QtQuick 2.12
import QtQuick.Window 2.12
import QtQuick.Controls 2.5
import QtQuick.Dialogs 1.3
import QtQuick.Layouts 1.12

ApplicationWindow {
    id: root
    visible: true
    title: qsTr("Two Stage IDS Tester")
    width: 640
    height: 640

    ListModel {
        id: activationFnModel
        ListElement { name: "ReLU" }
        ListElement { name: "ReLU 6" }
        ListElement { name: "CReLU" }
        ListElement { name: "ELU" }
        ListElement { name: "SELU" }
        ListElement { name: "Softplus" }
        ListElement { name: "Softsign" }
        ListElement { name: "Sigmoid" }
        ListElement { name: "Tanh" }
    }

    ListModel {
        id: lossReductionModel
        ListElement { name: "None" }
        ListElement { name: "Mean" }
        ListElement { name: "Sum" }
        ListElement { name: "Sum over Batch Size" }
        ListElement { name: "Sum over Nonzero Weights" }
        ListElement { name: "Sum by Nonzero Weights" }
    }

    ListModel {
        id: optimizerModel
        ListElement { name: "Adadelta Optimizer" }
        ListElement { name: "Adagrad DA Optimizer" }
        ListElement { name: "Adagrad Optimizer" }
        ListElement { name: "Adam Optimizer" }
        ListElement { name: "FTRL Optimizer" }
        ListElement { name: "Gradient Descent Optimizer" }
        ListElement { name: "Momentum Optimizer" }
        ListElement { name: "Proximal Adagrad Optimizer" }
        ListElement { name: "Proximal Gradient Descent Optimizer" }
        ListElement { name: "RMS Prop Optimizer" }
    }

    property var optimizerProperties: {
        "Adadelta Optimizer": {
            "Learning Rate": 0.001,
            "Rho": 0.95,
            "Epsilon": 1e-08
        },
        "Adagrad DA Optimizer": {
            "Learning Rate": 0.001,
            "Global Step": 0,
            "Initial Gradient Squared Accumulator Value": 0.1,
            "L1 Regularization Strength": 0.0,
            "L2 Regularization Strength": 0.0
        },
        "Adagrad Optimizer": {
            "Learning Rate": 0.001,
            "Initial Accumulator Value": 0.1
        },
        "Adam Optimizer": {
            "Learning Rate": 0.001,
            "Beta_1": 0.9,
            "Beta_2": 0.999,
            "Epsilon": 1e-08
        },
        "FTRL Optimizer": {
            "Learning Rate": 0.001,
            "Learning Rate Power": -0.5,
            "Initial Accumulator Value": 0.1,
            "L1 Regularization Strength": 0.0,
            "L2 Regularization Strength": 0.0,
            "L2 Shrinkage Regularization Strength": 0.0
        },
        "Gradient Descent Optimizer": {
            "Learning Rate": 0.001
        },
        "Momentum Optimizer": {
            "Learning Rate": 0.001,
            "Momentum": 0,
            "Use Nesterov": false
        },
        "Proximal Adagrad Optimizer": {
            "Learning Rate": 0.001,
            "Initial Accumulator Value": 0.1,
            "L1 Regularization Strength": 0.0,
            "L2 Regularization Strength": 0.0
        },
        "Proximal Gradient Descent Optimizer": {
            "Learning Rate": 0.001,
            "L1 Regularization Strength": 0.0,
            "L2 Regularization Strength": 0.0
        },
        "RMS Prop Optimizer": {
            "Learning Rate": 0.001,
            "Decay": 0.9,
            "Momentum": 0.0,
            "Centered": false
        }
    }

    Column {
        id: content
        TabBar {
            id: tabBar
            width: root.width
            height: contentHeight
            TabButton {
                width: implicitWidth + 10
                background.implicitHeight: 30
                text: qsTr("Process")
            }
            TabButton {
                width: implicitWidth + 10
                background.implicitHeight: 30
                text: qsTr("Train")
            }
            TabButton {
                width: implicitWidth + 10
                background.implicitHeight: 30
                text: qsTr("Test")
            }
        }

        StackLayout {
            anchors.top: tabBar.bottom
            anchors.topMargin: 10
            width: root.width - 20
            x: 10
            currentIndex: tabBar.currentIndex

            // Process Tab
            Item {
                Column {
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
                            LabeledTextField {
                                id: idprobsName
                                label: qsTr("ID Probs Name")
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
                            LabeledTextField {
                                id: datasetName
                                label: qsTr("Dataset Name")
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

            // Train Tab
            Item {
                Column {
                    GroupBox {
                        title: qsTr("Model")
                        Column {
                            spacing: 5
                            Button {
                                text: qsTr("New Model")
                                onClicked: newModelDialog.open()
                            }
                            Button {
                                text: qsTr("Load Model")
                            }
                            Button {
                                text: qsTr("Delete Model")
                            }
                        }
                    }
                }

                Dialog {
                    id: newModelDialog
                    title: qsTr("Create New Model")
                    standardButtons: StandardButton.Cancel | StandardButton.Ok
                    Component.onCompleted: newModelOptimizer.activated(0)
                    Column {
                        spacing: 5
                        LabeledTextField {
                            id: newModelName
                            label: qsTr("Name")
                        }
                        LabeledTextField {
                            id: newModelHiddenUnits
                            label: qsTr("Hidden Units")
                            field.validator: RegExpValidator {
                                regExp: /^\[(\d*\s*,\s*)*(\d+)\]$/
                            }
                            field.placeholderText: "[10, 10]"
                        }
                        Row {
                            spacing: 5
                            Label {
                                text: qsTr("Activation Function")
                                height: newModelActivationFn.height
                                verticalAlignment: Text.AlignVCenter
                            }
                            ComboBox {
                                id: newModelActivationFn
                                model: activationFnModel
                            }
                        }
                        Row {
                            spacing: 5
                            Label {
                                text: qsTr("Optimizer")
                                height: newModelOptimizer.height
                                verticalAlignment: Text.AlignVCenter
                            }
                            ComboBox {
                                id: newModelOptimizer
                                width: 200
                                model: optimizerModel
                                onActivated: {
                                    var currentOptimizerProps = root.optimizerProperties[currentText]
                                    optimizerPropertiesModel.clear()
                                    for (var prop in currentOptimizerProps) {
                                        if (currentOptimizerProps.hasOwnProperty(prop)) {
                                            var value = currentOptimizerProps[prop]
                                            optimizerPropertiesModel.append(
                                                {"name": prop, "type": typeof(value), "defaultValue": value, "value": value}
                                            )
                                        }
                                    }
                                }
                            }
                        }
                        ListModel {
                            id: optimizerPropertiesModel
                            dynamicRoles: true
                        }
                        GroupBox {
                            title: qsTr("Optimizer Properties")
                            width: 450
                            ListView {
                                id: optimizerPropertiesView
                                spacing: 5
                                implicitWidth: contentWidth
                                implicitHeight: contentHeight
                                model: optimizerPropertiesModel
                                delegate: optimizerPropertyDelegate

                                Component {
                                    id: optimizerPropertyDelegate
                                    Row {
                                        id: optimizerPropertyDelegateHolder
                                        spacing: 5
                                        Label {
                                            text: name
                                            height: textfield.height
                                            verticalAlignment: Text.AlignVCenter
                                        }
                                        CheckBox {
                                            id: checkbox
                                            checked: type == "boolean" ? defaultValue : false
                                            visible: type == "boolean"
                                            onCheckStateChanged: model.value = checked
                                        }
                                        TextField {
                                            id: textfield
                                            validator: DoubleValidator {}
                                            text: type == "number" ? defaultValue : ""
                                            visible: type == "number"
                                            onTextChanged: {
                                                if (acceptableInput) {
                                                    model.value = text
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }



                        Row {
                            spacing: 5
                            Label {
                                text: qsTr("Loss Reduction")
                                height: newModelActivationFn.height
                                verticalAlignment: Text.AlignVCenter
                            }
                            ComboBox {
                                id: newModelLossReduction
                                width: 200
                                model: lossReductionModel
                                currentIndex: 2
                            }
                        }
                    }
                    onAccepted: {
                        for (var i = 0; i < optimizerPropertiesModel.count; i++) {
                            var prop = optimizerPropertiesModel.get(i)
                            console.log(prop.name, prop.value)
                        }
                    }
                }
            }

            // Test Tab
            Item {
                anchors.fill: parent
            }
        }
    }
}


