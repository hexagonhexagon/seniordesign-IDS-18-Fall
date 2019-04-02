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
    ListModel {
        id: fileSelectionsModel
        ListElement { fileName: "No File Selected" }
    }

    Column {
        anchors.margins: 20
        anchors.fill: parent
        spacing: 5
        Row {
            spacing: 5
            Button {
                id: testFileSelectButton
                text: qsTr("File Select")
                onClicked: fileDialog.open()
            }

            ListView {
                id: fileDisplay
                boundsBehavior: Flickable.StopAtBounds
                spacing: 5
                width: 100
                height: contentHeight
                model: fileSelectionsModel
                delegate: fileDelegate
            }
        }

        Row {
            spacing: 5
            Label {
                text: "ID Probs Name"
                height: idProbsName.height
                verticalAlignment: Text.AlignVCenter
            }
            TextField {
                id: idProbsName
            }
        }

        Button {
            id: generateIDProbsButton
            text: qsTr("Make ID Probs File")
            onClicked: dpManager.create_idprobs_file(fileDialog.fileUrls, idProbsName.text)
        }
    }

    Component {
        id: fileDelegate
        Text {
            width: 200
            text: fileName
            elide: Text.ElideRight
        }
    }



    FileDialog {
        id: fileDialog
        title: qsTr("Multi-select test")
        nameFilters: "CAN Frame Files (*.json *.traffic *.csv)"
        selectMultiple: true
        onAccepted: {
            fileSelectionsModel.clear()
            for (var i = 0; i < fileUrls.length; i++) {
                var urlString = fileUrls[i].toString();
                var fileName = urlString.slice(urlString.lastIndexOf("/")+1, fileUrl.length);
                fileSelectionsModel.append({"fileName": fileName})
            }
        }
    }
}
