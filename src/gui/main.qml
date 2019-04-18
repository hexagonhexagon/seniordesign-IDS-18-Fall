import QtQuick 2.12
import QtQuick.Window 2.12
import QtQuick.Controls 2.5
import QtQuick.Dialogs 1.3
import QtQuick.Layouts 1.12

ApplicationWindow {
    id: root
    visible: true
    title: qsTr("Two Stage IDS Tester")
    width: 1550
    height: 850

    property double speedometerRotationAngle: -136;
    property double tachometerRotationAngle: -103;

    // Bools to keep track of whether an indicator light is on or off
    property bool oilLightOn: false;
    property bool batteryLightOn: false;
    property bool fluidLightOn: false;
    property bool highBeamLightOn: false;
    property bool seatBeltLightOn: false;
    property bool engineLightOn: false;
    property bool airbagLightOn: false;
    property bool lowBeamLightOn: false;
    property bool tempLightOn: false;
    property bool absLightOn: false;
    property bool brakeLightOn: false;
    property bool tractionLightOn: false;

    // Bools and timer for turn signals and hazards -- turn signals blink once per second
    property bool rightTurnLightOn: false;  // Indicates if light is currently lit
    property bool leftTurnLightOn: false;
    property bool rightTurnLightActivated: false; // Indicates if light is currently activated (blinking)
    property bool leftTurnLightActivated: false;
    property bool hazardsActivated: false;
    property double startTime: 0;   // Time that blinker/hazards were last lit at

    signal judgeResult(variant result)
    Component.onCompleted: {
        simManager.result.connect(judgeResult)
    }

    Connections {
        target: root
        onJudgeResult: {
            reportManager.update_statistics(result)
            outputLogModel.append(result)
        }
    }

    Connections {
        target: reportManager
        onStatisticsChanged: reportModel.updateReport()
    }


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
                                id: idprobsFileSelectProcess
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
                                onClicked: dpManager.create_idprobs_file(idprobsFileSelectProcess.fileUrls, idprobsName.text)
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
                                    id: datasetIdprobsProcess
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
                                    id: noAttackSliderProcess
                                    label: qsTr("No Attack")
                                    value: 0.5
                                    // If the no attack slider is moved, proportionally
                                    // scale up or down all other attacks to ensure the
                                    // probabilities sum to 1.
                                    onMoved: {
                                        // Get (1 - previous slider value).
                                        var attackValueSum =  randomSliderProcess.value +
                                                floodSliderProcess.value + replaySliderProcess.value +
                                                spoofSliderProcess.value
                                        if (attackValueSum == 0.0) {
                                            // If sum was 0, scale up other slider values equally.
                                            var newValue = (1 - value) / 4
                                            randomSliderProcess.value = newValue
                                            floodSliderProcess.value = newValue
                                            replaySliderProcess.value = newValue
                                            spoofSliderProcess.value = newValue
                                        }
                                        else {
                                            // Otherwise, scale up other slider values by
                                            // multiplying by (1 - new value) / (1 - old
                                            // value), which ensures everything sums to 1.
                                            var multiplier = (1 - value) / attackValueSum
                                            randomSliderProcess.value *= multiplier
                                            floodSliderProcess.value *= multiplier
                                            replaySliderProcess.value *= multiplier
                                            spoofSliderProcess.value *= multiplier
                                        }
                                    }
                                }
                                MaliciousGeneratorSlider {
                                    id: randomSliderProcess
                                    label: qsTr("Random Attack")
                                    value: 0.125
                                    // If a non-no attack slider is moved, adjust the
                                    // No Attack slider up or down relative to the new value of
                                    // this slider. If No Attack is brought to 0, this slider
                                    // cannot be moved any further to the right. The code is
                                    // very similar for the 3 sliders after this one.
                                    onMoved: {
                                        // Find the sum of all the other attacks.
                                        var otherValueSum =  floodSliderProcess.value + replaySliderProcess.value + spoofSliderProcess.value
                                        if (value + otherValueSum <= 1.0)  {
                                            // Is the new sum of the attack probabilities
                                            // less than 1? If so, we adjust the No Attack
                                            // slider accordingly.
                                            noAttackSliderProcess.value = 1 - value - otherValueSum
                                        }
                                        else {
                                            // Otherwise, No Attack is at 0 and we set this
                                            // slider value to the highest it can be without
                                            // getting the probabilities to sum greater than
                                            // 1.
                                            noAttackSliderProcess.value = 0.0
                                            value = 1 - otherValueSum
                                        }
                                    }
                                }
                                MaliciousGeneratorSlider {
                                    id: floodSliderProcess
                                    label: qsTr("Flood Attack")
                                    value: 0.125
                                    onMoved: {
                                        var otherValueSum =  randomSliderProcess.value + replaySliderProcess.value + spoofSliderProcess.value
                                        if (value + otherValueSum <= 1.0)  {
                                            noAttackSliderProcess.value = 1 - value - otherValueSum
                                        }
                                        else {
                                            noAttackSliderProcess.value = 0.0
                                            value = 1 - otherValueSum
                                        }
                                    }
                                }
                                MaliciousGeneratorSlider {
                                    id: replaySliderProcess
                                    label: qsTr("Replay Attack")
                                    value: 0.125
                                    onMoved: {
                                        var otherValueSum =  randomSliderProcess.value + floodSliderProcess.value + spoofSliderProcess.value
                                        if (value + otherValueSum <= 1.0)  {
                                            noAttackSliderProcess.value = 1 - value - otherValueSum
                                        }
                                        else {
                                            noAttackSliderProcess.value = 0.0
                                            value = 1 - otherValueSum
                                        }
                                    }
                                }
                                MaliciousGeneratorSlider {
                                    id: spoofSliderProcess
                                    label: qsTr("Spoofing Attack")
                                    value: 0.125
                                    onMoved: {
                                        var otherValueSum =  randomSliderProcess.value + floodSliderProcess.value + replaySliderProcess.value
                                        if (value + otherValueSum <= 1.0)  {
                                            noAttackSliderProcess.value = 1 - value - otherValueSum
                                        }
                                        else {
                                            noAttackSliderProcess.value = 0.0
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
                                        "none": noAttackSliderProcess.value,
                                        "random": randomSliderProcess.value,
                                        "flood": floodSliderProcess.value,
                                        "replay": replaySliderProcess.value,
                                        "spoof": spoofSliderProcess.value
                                    }
                                    // Call the function. We get the file selected via
                                    // SingleFileSelect.fileUrl, and we pass in the
                                    // adjustments we just specified.
                                    dpManager.create_dataset(datasetFileSelect.fileUrl, datasetIdprobsProcess.currentText, malgenSettings, datasetName.text)
                                }
                            }
                        }
                    }
                }
            }

            // Train Tab
            Item {
                Row {
                    spacing: 5
                    Column {
                        spacing: 5
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
                                    onClicked: loadModelDialog.open()
                                }
                                Button {
                                    text: qsTr("Delete Model")
                                    onClicked: deleteModelDialog.open()
                                }
                            }
                        }

                        GroupBox {
                            title: qsTr("Train Rules Based IDS")
                            Column {
                                spacing: 5
                                Row {
                                    spacing: 5
                                    Label {
                                        text: qsTr("Dataset to Use")
                                    }

                                    ComboBox {
                                        id: rulesTrainingDataset
                                        model: dpManager.availableDatasets
                                    }
                                }

                                Button {
                                    text: qsTr("Train")
                                    onClicked: {
                                        idsManager.train_rules(rulesTrainingDataset.currentText)
                                    }
                                }
                            }
                        }

                        GroupBox {
                            title: qsTr("Train DNN Based IDS")
                            Column {
                                spacing: 5
                                Row {
                                    spacing: 5
                                    Label {
                                        text: qsTr("Dataset to Use")
                                    }

                                    ComboBox {
                                        id: dnnTrainingDataset
                                        model: dpManager.availableDatasets
                                    }
                                }

                                LabeledTextField {
                                    id: dnnTrainingNumSteps
                                    label: qsTr("Number of Steps")
                                    field.validator: IntValidator {
                                        bottom: 1
                                    }
                                }

                                Button {
                                    text: qsTr("Train")
                                    onClicked: {
                                        idsManager.train_dnn(rulesTrainingDataset.currentText, dnnTrainingNumSteps.text)
                                    }
                                }
                            }
                        }
                    }

                    GroupBox {
                        id: modelPropertiesDisplay
                        title: qsTr("Model Details")
                        Column {
                            spacing: 5
                            Label {
                                text: "Model Name: " + idsManager.parameters["Model Name"]
                            }
                            Label {
                                text: "Rules Trained: " + idsManager.parameters["Rules Trained"]
                            }
                            Label {
                                text: "DNN Trained: " + idsManager.parameters["DNN Trained"]
                            }
                            Label {
                                text: "Hidden Units: " + idsManager.parameters["Hidden Units"]
                            }
                            Label {
                                text: "Activation Function: " + idsManager.parameters["Activation Function"]
                            }
                            Label {
                                text: "Optimizer: " + idsManager.parameters["Optimizer"]
                            }
                            Label {
                                text: "Loss Reduction: " + idsManager.parameters["Loss Reduction"]
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
                                            optimizerPropertiesModel.append({
                                                "name": prop,
                                                "type": typeof(value),
                                                "defaultValue": value,
                                                "value": value
                                            })
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
                        var properties = {
                            "Hidden Units": newModelHiddenUnits.text,
                            "Activation Function": newModelActivationFn.currentText,
                            "Optimizer": newModelOptimizer.currentText,
                            "Loss Reduction": newModelLossReduction.currentText
                        }
                        idsManager.new_model(newModelName.text, properties)

                        for (var i = 0; i < optimizerPropertiesModel.count; i++) {
                            var prop = optimizerPropertiesModel.get(i)
                            console.log(typeof(prop))
                            console.log(prop.name, prop.value)
                        }
                    }
                }

                Dialog {
                    id: loadModelDialog
                    title: qsTr("Load Model")
                    standardButtons: StandardButton.Cancel | StandardButton.Ok

                    Row {
                        spacing: 5
                        Label {
                            text: qsTr("Model to Load")
                            height: loadModelModel.height
                            verticalAlignment: Text.AlignVCenter
                        }
                        ComboBox {
                            id: loadModelModel
                            model: idsManager.availableModels
                        }
                    }

                    onAccepted: {
                        idsManager.load_model(loadModelModel.currentText)
                    }
                }

                Dialog {
                    id: deleteModelDialog
                    title: qsTr("Delete Model")
                    standardButtons: StandardButton.Cancel | StandardButton.Ok

                    Row {
                        spacing: 5
                        Label {
                            text: qsTr("Model to Delete")
                            height: loadModelModel.height
                            verticalAlignment: Text.AlignVCenter
                        }
                        ComboBox {
                            id: deleteModelModel
                            model: idsManager.availableModels
                        }
                    }

                    onAccepted: {
                        idsManager.delete_model(loadModelModel.currentText)
                    }
                }
            }

            // Test Tab
            Item {
                Row {
                    spacing: 5
                    Column {
                        spacing: 5
                        //Test Setup - used to load Idprobs file and CAN Frame File and start test
                        GroupBox {
                            title: qsTr("Test Setup")
                            Column {
                                spacing: 5
                                //Select Idprobs file
                                Row {
                                    spacing: 5
                                    Label {
                                        text: qsTr("ID Probs to Use")
                                    }

                                    ComboBox {
                                        id: datasetIdprobsTest
                                        model: dpManager.availableIdprobs
                                    }
                                }

                                //Select CAN Frame File
                                SingleFileSelect {
                                    id: canFrameFile
                                    title: qsTr("Select CAN Frame File")
                                    nameFilters: "CAN Frame Files (*.json *.traffic *.csv)"
                                }

                                Button {
                                    id: startButton
                                    text: qsTr("Start Test (temporary)")
                                    onClicked: {
                                        var malgenSettings = {
                                            "none": noAttackSliderTest.value,
                                            "random": randomSliderTest.value,
                                            "flood": floodSliderTest.value,
                                            "replay": replaySliderTest.value,
                                            "spoof": spoofSliderTest.value
                                        }
                                        simManager.adjust_malgen(malgenSettings)
                                        simManager.start_simulation(canFrameFile.fileUrl, datasetIdprobsTest.currentText)
                                        enabled = false
                                        nextButton.enabled = true
                                        stopButton.enabled = true
                                    }
                                }

                                Button {
                                    id: nextButton
                                    text: qsTr("Judge Next Frame (temporary)")
                                    enabled: false
                                    onClicked: {
                                        simManager.judge_next_frame()
                                    }
                                }

                                Button {
                                    id: stopButton
                                    text: qsTr("Stop simulation (temporary)")
                                    enabled: false
                                    onClicked: {
                                        simManager.stop_simulation()
                                        enabled = false
                                        nextButton.enabled = false
                                        startButton.enabled = true
                                        reportManager.reset_statistics()
                                        outputLogModel.clear()
                                    }
                                }
                            }
                        }

                        //Report - used to output results of test and save results
                        GroupBox {
                            title: qsTr("Report")

                            Column {
                                spacing: 5

                                ListModel {
                                    id: reportModel

                                    function updateReport() {
                                        reportModel.clear()
                                        var stats = reportManager.statistics
                                        for (var i = 0; i < stats.length; i++) {
                                            reportModel.append(stats[i])
                                        }
                                    }
                                }

                                ListView {
                                    spacing: 5
                                    implicitWidth: contentWidth
                                    implicitHeight: contentHeight
                                    model: reportModel
                                    delegate: reportDelegate

                                    Component.onCompleted: reportModel.updateReport()
                                }

                                Component {
                                    id: reportDelegate
                                    Text {
                                        text: stat + ": " + (value*100).toFixed(2).toString() + '%'
                                    }
                                }

                                //Save CAN Log Checkbox - only include CAN Log in csv saved
                                //if checkbox is checked
                                CheckBox {
                                    id: saveCANLog
                                    text: qsTr("Save CAN Log with Results")
                                }
                                //Save Results button - prompts a file dialog to pick a
                                //path and filename to save the results to and saves them.
                                SingleSaveFileSelect {
                                    id: saveResultsFile
                                    title: qsTr("Save Results")
                                    nameFilters: "CAN Frame Files (*.json *.traffic *.csv)"
                                }
                                //Save Button
                                Button {
                                    id: saveResultsButton
                                    text: qsTr("Save Results")
                                }
                            }
                        }
                    }
                    Column {
                        //Visualizer
                        GroupBox {
                            title: qsTr("Visualizer")
                            width: 860
                            height: 475
                            Image
                            {
                                id: background
                                anchors.fill: parent
                                fillMode: Image.Stretch
                                source: "assets/Background.png"
                                Image
                                {
                                    id: fuelGauge

                                    x: 447
                                    y: 67
                                    width: 277
                                    height: 198
                                    fillMode: Image.PreserveAspectFit
                                    source: "assets/fuelGauge.png"

                                    Image
                                    {
                                        id: fuelSupport
                                        x: 123
                                        y: 83
                                        width: 44
                                        height: 33
                                        fillMode: Image.PreserveAspectFit
                                        source: "assets/supportSmall.png"
                                    }
                                }

                                Image
                                {
                                    id: tempGauge
                                    x: 133
                                    y: 86
                                    width: 250
                                    height: 160
                                    fillMode: Image.PreserveAspectFit
                                    source: "assets/tempGauge.png"

                                    Image {
                                        id: tempSupport
                                        x: 97
                                        y: 64
                                        width: 44
                                        height: 33
                                        fillMode: Image.PreserveAspectFit
                                        source: "assets/supportSmall.png"
                                    }
                                }
                            }

                            Image
                            {
                                id: lightBackground
                                x: 193
                                y: 154
                                width: 457
                                height: 353
                                fillMode: Image.Stretch
                                source: "assets/BackgroundLights.png"

                                Image
                                {
                                    id: oilLight
                                    x: 106
                                    y: 96
                                    width: 55
                                    height: 41
                                    visible: oilLightOn
                                    z: 1
                                    fillMode: Image.PreserveAspectFit
                                    source: "assets/OilLight.png"
                                }

                                Image
                                {
                                    id: batteryLight
                                    x: 174
                                    y: 96
                                    width: 55
                                    height: 41
                                    visible: batteryLightOn
                                    z: 1
                                    fillMode: Image.PreserveAspectFit
                                    source: "assets/BatteryLight.png"
                                }

                                Image
                                {
                                    id: fluidLight
                                    x: 235
                                    y: 96
                                    width: 55
                                    height: 41
                                    visible: fluidLightOn
                                    z: 1
                                    fillMode: Image.PreserveAspectFit
                                    source: "assets/FluidLight.png"
                                }

                                Image
                                {
                                    id: lowbeamLight
                                    x: 296
                                    y: 151
                                    width: 55
                                    height: 41
                                    visible: lowBeamLightOn
                                    z: 1
                                    fillMode: Image.PreserveAspectFit
                                    source: "assets/LowbeamLight.png"
                                }

                                Image
                                {
                                    id: seatbeltLight
                                    x: 106
                                    y: 143
                                    width: 55
                                    height: 49
                                    visible: seatBeltLightOn
                                    z: 1
                                    fillMode: Image.PreserveAspectFit
                                    source: "assets/SeatbeltLight.png"
                                }

                                Image
                                {
                                    id: engineLight
                                    x: 174
                                    y: 143
                                    width: 55
                                    height: 49
                                    visible: engineLightOn
                                    z: 1
                                    fillMode: Image.PreserveAspectFit
                                    source: "assets/EngineLight.png"
                                }

                                Image
                                {
                                    id: airbagLight
                                    x: 235
                                    y: 143
                                    width: 55
                                    height: 49
                                    visible: airbagLightOn
                                    z: 1
                                    fillMode: Image.PreserveAspectFit
                                    source: "assets/AirbagLight.png"
                                }

                                Image
                                {
                                    id: highbeamLight
                                    x: 296
                                    y: 88
                                    width: 55
                                    height: 49
                                    visible: highBeamLightOn
                                    z: 1
                                    fillMode: Image.PreserveAspectFit
                                    source: "assets/HighbeamLight.png"
                                }

                                Image
                                {
                                    id: tempLight
                                    x: 106
                                    y: 208
                                    width: 55
                                    height: 49
                                    visible: tempLightOn
                                    z: 1
                                    fillMode: Image.PreserveAspectFit
                                    source: "assets/TempLight.png"
                                }

                                Image
                                {
                                    id: absLight
                                    x: 174
                                    y: 208
                                    width: 55
                                    height: 49
                                    visible: absLightOn
                                    z: 1
                                    fillMode: Image.PreserveAspectFit
                                    source: "assets/ABSLight.png"
                                }

                                Image
                                {
                                    id: parkingBrakeLight
                                    x: 235
                                    y: 208
                                    width: 55
                                    height: 49
                                    visible: brakeLightOn
                                    z: 1
                                    fillMode: Image.PreserveAspectFit
                                    source: "assets/ParkingBrakeLight.png"
                                }

                                Image
                                {
                                    id: tractionLight
                                    x: 296
                                    y: 208
                                    width: 55
                                    height: 49
                                    visible: tractionLightOn
                                    z: 1
                                    fillMode: Image.PreserveAspectFit
                                    source: "assets/TractionLight.png"
                                }

                                Image
                                {
                                    id: oilOff
                                    x: 109
                                    y: 96
                                    width: 49
                                    height: 41
                                    fillMode: Image.PreserveAspectFit
                                    source: "assets/OilOff.png"
                                }

                                Image
                                {
                                    id: batteryOff
                                    x: 177
                                    y: 96
                                    width: 50
                                    height: 41
                                    fillMode: Image.PreserveAspectFit
                                    source: "assets/BatteryOff.png"
                                }

                                Image
                                {
                                    id: fluidOff
                                    x: 235
                                    y: 96
                                    width: 55
                                    height: 41
                                    fillMode: Image.PreserveAspectFit
                                    source: "assets/FluidOff.png"
                                }

                                Image
                                {
                                    id: highbeamOff
                                    x: 300
                                    y: 88
                                    width: 48
                                    height: 49
                                    fillMode: Image.PreserveAspectFit
                                    source: "assets/HighbeamOff.png"
                                }

                                Image
                                {
                                    id: seatbeltOff
                                    x: 108
                                    y: 145
                                    width: 52
                                    height: 45
                                    fillMode: Image.PreserveAspectFit
                                    source: "assets/SeatbeltOff.png"
                                }

                                Image
                                {
                                    id: engineOff
                                    x: 174
                                    y: 143
                                    width: 55
                                    height: 49
                                    fillMode: Image.PreserveAspectFit
                                    source: "assets/EngineOff.png"
                                }

                                Image
                                {
                                    id: airbagOff
                                    x: 235
                                    y: 147
                                    width: 55
                                    height: 41
                                    fillMode: Image.PreserveAspectFit
                                    source: "assets/AirbagOff.png"
                                }

                                Image
                                {
                                    id: lowbeamOff
                                    x: 298
                                    y: 151
                                    width: 52
                                    height: 41
                                    fillMode: Image.PreserveAspectFit
                                    source: "assets/LowbeamOff.png"
                                }

                                Image
                                {
                                    id: tempOff
                                    x: 106
                                    y: 208
                                    width: 55
                                    height: 49
                                    fillMode: Image.PreserveAspectFit
                                    source: "assets/TempOff.png"
                                }

                                Image
                                {
                                    id: absOff
                                    x: 174
                                    y: 208
                                    width: 55
                                    height: 49
                                    fillMode: Image.PreserveAspectFit
                                    source: "assets/ABSOff.png"
                                }

                                Image
                                {
                                    id: parkingBrakeOff
                                    x: 235
                                    y: 208
                                    width: 55
                                    height: 49
                                    fillMode: Image.PreserveAspectFit
                                    source: "assets/ParkingBrakeOff.png"
                                }

                                Image
                                {
                                    id: tractionOff
                                    x: 296
                                    y: 208
                                    width: 55
                                    height: 49
                                    fillMode: Image.PreserveAspectFit
                                    source: "assets/TractionOff.png"
                                }
                            }

                            Image
                            {
                                id: speedometer
                                x: -54
                                y: 95
                                width: 391
                                height: 347
                                antialiasing: true
                                rotation: 0
                                fillMode: Image.PreserveAspectFit
                                source: "assets/Speedometer.png"


                                Image
                                {
                                    id: speedNeedle
                                    x: 191
                                    y: 61
                                    width: 11
                                    height: 113
                                    rotation: speedometerRotationAngle
                                    antialiasing: true
                                    transformOrigin: Item.Bottom
                                    fillMode: Image.Stretch
                                    source: "assets/NeedleLarge.png"
                                    smooth: true
                                }

                                Image
                                {
                                    id: speedSupport
                                    x: 175
                                    y: 155
                                    width: 42
                                    height: 37
                                    antialiasing: true
                                    fillMode: Image.PreserveAspectFit
                                    source: "assets/SupportLarge.png"
                                }
                            }


                            Image
                            {
                                id: tachometer
                                x: 507
                                y: 95
                                width: 391
                                height: 347
                                fillMode: Image.PreserveAspectFit
                                antialiasing: true
                                Image
                                {
                                    id: tachNeedle
                                    x: 191
                                    y: 61
                                    width: 11
                                    height: 113
                                    rotation: tachometerRotationAngle
                                    fillMode: Image.Stretch
                                    transformOrigin: Item.Bottom
                                    antialiasing: true
                                    smooth: true
                                    source: "assets/NeedleLarge.png"
                                }

                                Image
                                {
                                    id: tachSupport
                                    x: 175
                                    y: 155
                                    width: 42
                                    height: 37
                                    fillMode: Image.PreserveAspectFit
                                    antialiasing: true
                                    source: "assets/SupportLarge.png"
                                }

                                source: "assets/Tachometer.png"
                                rotation: 0
                            }


                            Image
                            {
                                id: turnBackground
                                x: 117
                                y: 11
                                width: 609
                                height: 298
                                fillMode: Image.PreserveAspectFit
                                source: "assets/turnBackground.png"

                                Image
                                {
                                    id: turnLeftOff
                                    x: 240
                                    y: 121
                                    width: 52
                                    height: 56
                                    fillMode: Image.PreserveAspectFit
                                    source: "assets/turnLeftOff.png"
                                }

                                Image
                                {
                                    id: turnRightOff
                                    x: 321
                                    y: 119
                                    width: 53
                                    height: 60
                                    fillMode: Image.PreserveAspectFit
                                    source: "assets/turnRightOff.png"
                                }

                                Image
                                {
                                    id: turnLeftOn
                                    objectName: "leftTurnSignal"
                                    x: 236
                                    y: 118
                                    width: 59
                                    height: 63
                                    visible: leftTurnLightOn
                                    fillMode: Image.PreserveAspectFit
                                    source: "assets/turnLeftLight.png"
                                }

                                Image
                                {
                                    id: turnRightOn
                                    x: 318
                                    y: 116
                                    width: 59
                                    height: 63
                                    visible: false
                                    fillMode: Image.PreserveAspectFit
                                    source: "assets/turnRightLight.png"
                                }

                                Timer
                                {
                                    interval: 1000;
                                    running: rightTurnLightActivated || leftTurnLightActivated || hazardsActivated;
                                    repeat: true
                                    onTriggered:
                                    {
                                        if(rightTurnLightActivated)
                                        {
                                            rightTurnLightOn ? rightTurnLightOn = false : rightTurnLightOn = true;
                                            turnRightOn.visible = rightTurnLightOn
                                        }

                                        if(leftTurnLightActivated)
                                        {
                                            leftTurnLightOn ? leftTurnLightOn = false : leftTurnLightOn = true;
                                            turnLeftOn.visible = leftTurnLightOn
                                        }

                                        if(hazardsActivated)
                                        {
                                            leftTurnLightOn ? leftTurnLightOn = false : leftTurnLightOn = true;
                                            rightTurnLightOn ? rightTurnLightOn = false : rightTurnLightOn = true;
                                            turnLeftOn.visible = leftTurnLightOn
                                            turnRightOn.visible = rightTurnLightOn
                                        }
                                    }
                                }
                            }
                        }

                        //Messages
                        GroupBox{
                            width: 860
                            height: 300
                            title: qsTr("Messages")
                            TabBar {
                                id: tabBarTestOutput
                                height: contentHeight
                                TabButton {
                                    width: implicitWidth + 10
                                    background.implicitHeight: 30
                                    text: qsTr("Output")
                                }
                                TabButton {
                                    width: implicitWidth + 10
                                    background.implicitHeight: 30
                                    text: qsTr("Filter")
                                }
                            }

                            StackLayout {
                                anchors.top: tabBarTestOutput.bottom
                                anchors.topMargin: 30
                                anchors.fill: parent
                                currentIndex: tabBarTestOutput.currentIndex

                                //Output Tab
                                Item {
                                    anchors.fill: parent
                                    anchors.margins: 5

                                    ListView {
                                        id: outputLogView
                                        spacing: 5
                                        width: parent.width
                                        height: parent.height
                                        model: outputLogModel
                                        delegate: outputLogDelegate
                                        ScrollBar.vertical: ScrollBar {
                                            parent: outputLogView.parent
                                            anchors.top: parent.top
                                            anchors.left: parent.right
                                            anchors.bottom: parent.bottom
                                        }
                                    }

                                    Component {
                                        id: outputLogDelegate

                                        Text {
                                            text: label.charAt(0).toUpperCase() + label.slice(1) + " Frame, ID " + frame["id"] + " marked as " + (judgement ? "malicious" : "benign") + (reason ? " by " + reason : "") + "."
                                        }
                                    }
                                }

                                //Filter Tab
                                Item {
                                    Row{
                                        spacing: 5
                                        //Result Type
                                        Column{
                                            spacing: 5

                                            //False Negative
                                            CheckBox {
                                                id: falseNegativeFilter
                                                text: "False Negative"
                                                checked: true
                                                onCheckedChanged: outputLogModel.change_filter("false_negative", checked)
                                            }
                                            //False Positive
                                            CheckBox {
                                                id: falsePositiveFilter
                                                text: "False Positive"
                                                checked: true
                                                onCheckedChanged: outputLogModel.change_filter("false_positive", checked)
                                            }
                                            //True Positive
                                            CheckBox {
                                                id: truePositiveFilter
                                                text: "True Positive"
                                                checked: true
                                                onCheckedChanged: outputLogModel.change_filter("true_positive", checked)
                                            }
                                            //True Negative
                                            CheckBox {
                                                id: trueNegativeFilter
                                                text: "True Negative"
                                                checked: true
                                                onCheckedChanged: outputLogModel.change_filter("true_negative", checked)
                                            }
                                        }

                                        //Message Type
                                        Column{
                                            spacing: 5

                                            //benign
                                            CheckBox {
                                                id: benignFilter
                                                text: "Benign"
                                                checked: true
                                                onCheckedChanged: outputLogModel.change_filter("benign", checked)
                                            }
                                            //random
                                            CheckBox {
                                                id: randomFilter
                                                text: "Random"
                                                checked: true
                                                onCheckedChanged: outputLogModel.change_filter("random", checked)
                                            }
                                            //flood
                                            CheckBox {
                                                id: floodFilter
                                                text: "Flood"
                                                checked: true
                                                onCheckedChanged: outputLogModel.change_filter("flood", checked)
                                            }
                                            //replay
                                            CheckBox {
                                                id: replayFilter
                                                text: "Replay"
                                                checked: true
                                                onCheckedChanged: outputLogModel.change_filter("replay", checked)
                                            }
                                            //spoofing
                                            CheckBox {
                                                id: spoofingFilter
                                                text: "Spoofing"
                                                checked: true
                                                onCheckedChanged: outputLogModel.change_filter("spoof", checked)
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }

                    Column{
                        //Attack Controls
                        GroupBox{
                            title: qsTr("Attack Controls")
                            Column{
                                anchors.fill: parent
                                MaliciousGeneratorSlider {
                                    id: noAttackSliderTest
                                    label: qsTr("No Attack")
                                    value: 0.5
                                    // If the no attack slider is moved, proportionally
                                    // scale up or down all other attacks to ensure the
                                    // probabilities sum to 1.
                                    onMoved: {
                                        // Get (1 - previous slider value).
                                        var attackValueSum =  randomSliderTest.value +
                                                floodSliderTest.value + replaySliderTest.value +
                                                spoofSliderTest.value
                                        if (attackValueSum == 0.0) {
                                            // If sum was 0, scale up other slider values equally.
                                            var newValue = (1 - value) / 4
                                            randomSliderTest.value = newValue
                                            floodSliderTest.value = newValue
                                            replaySliderTest.value = newValue
                                            spoofSliderTest.value = newValue
                                        }
                                        else {
                                            // Otherwise, scale up other slider values by
                                            // multiplying by (1 - new value) / (1 - old
                                            // value), which ensures everything sums to 1.
                                            var multiplier = (1 - value) / attackValueSum
                                            randomSliderTest.value *= multiplier
                                            floodSliderTest.value *= multiplier
                                            replaySliderTest.value *= multiplier
                                            spoofSliderTest.value *= multiplier
                                        }
                                    }
                                }
                                MaliciousGeneratorSlider {
                                    id: randomSliderTest
                                    label: qsTr("Random Attack")
                                    value: 0.125
                                    // If a non-no attack slider is moved, adjust the
                                    // No Attack slider up or down relative to the new value of
                                    // this slider. If No Attack is brought to 0, this slider
                                    // cannot be moved any further to the right. The code is
                                    // very similar for the 3 sliders after this one.
                                    onMoved: {
                                        // Find the sum of all the other attacks.
                                        var otherValueSum =  floodSliderTest.value + replaySliderTest.value + spoofSliderTest.value
                                        if (value + otherValueSum <= 1.0)  {
                                            // Is the new sum of the attack probabilities
                                            // less than 1? If so, we adjust the No Attack
                                            // slider accordingly.
                                            noAttackSliderTest.value = 1 - value - otherValueSum
                                        }
                                        else {
                                            // Otherwise, No Attack is at 0 and we set this
                                            // slider value to the highest it can be without
                                            // getting the probabilities to sum greater than
                                            // 1.
                                            noAttackSliderTest.value = 0.0
                                            value = 1 - otherValueSum
                                        }
                                    }
                                }
                                MaliciousGeneratorSlider {
                                    id: floodSliderTest
                                    label: qsTr("Flood Attack")
                                    value: 0.125
                                    onMoved: {
                                        var otherValueSum =  randomSliderTest.value + replaySliderTest.value + spoofSliderTest.value
                                        if (value + otherValueSum <= 1.0)  {
                                            noAttackSliderTest.value = 1 - value - otherValueSum
                                        }
                                        else {
                                            noAttackSliderTest.value = 0.0
                                            value = 1 - otherValueSum
                                        }
                                    }
                                }
                                MaliciousGeneratorSlider {
                                    id: replaySliderTest
                                    label: qsTr("Replay Attack")
                                    value: 0.125
                                    onMoved: {
                                        var otherValueSum =  randomSliderTest.value + floodSliderTest.value + spoofSliderTest.value
                                        if (value + otherValueSum <= 1.0)  {
                                            noAttackSliderTest.value = 1 - value - otherValueSum
                                        }
                                        else {
                                            noAttackSliderTest.value = 0.0
                                            value = 1 - otherValueSum
                                        }
                                    }
                                }
                                MaliciousGeneratorSlider {
                                    id: spoofSliderTest
                                    label: qsTr("Spoofing Attack")
                                    value: 0.125
                                    onMoved: {
                                        var otherValueSum =  randomSliderTest.value + floodSliderTest.value + replaySliderTest.value
                                        if (value + otherValueSum <= 1.0)  {
                                            noAttackSliderTest.value = 1 - value - otherValueSum
                                        }
                                        else {
                                            noAttackSliderTest.value = 0.0
                                            value = 1 - otherValueSum
                                        }
                                    }
                                }
                            }
                        }

                        //Time Controls
                        GroupBox{
                            title: qsTr("Time Control")

                            Row{
                                anchors.fill: parent

                                //Backward Button
                                Button{
                                    height: 70
                                    width: 70

                                    Image{
                                        id: backward
                                        anchors.fill: parent
                                        source: "assets/backward.png"
                                    }
                                }

                                //Pause Button
                                Button{
                                    height: 70
                                    width: 70

                                    Image{
                                        id: pause
                                        anchors.fill: parent
                                        source: "assets/pause.png"
                                    }
                                }

                                //Play Button
                                Button{
                                    height: 70
                                    width: 70

                                    Image{
                                        id: play
                                        anchors.fill: parent
                                        source: "assets/play.png"
                                    }
                                }

                                //Forward Button
                                Button{
                                    height: 70
                                    width: 70

                                    Image{
                                        id: forward
                                        anchors.fill: parent
                                        source: "assets/forward.png"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
