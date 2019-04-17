import QtQuick 2.12
import QtQuick.Window 2.12
import QtQuick.Controls 2.5
import QtQuick.Dialogs 1.3

Item {
    id: root
    // An Item by default has 0 width and 0 height, so anything after it would
    // overlap on top of it. This is fixed by setting a height and width.
    width: holder.width
    height: holder.height
    property alias title: fileDialog.title
    property alias nameFilters: fileDialog.nameFilters
    property alias fileUrl: fileDialog.fileUrl

    Row {
        id: holder
        spacing: 5
        // Actual file select button. Activates the FileDialog, which actually
        // allows files to be selected.
        Button {
            id: fileSelectButton
            text: qsTr("File Select")
            onClicked: fileDialog.open()
        }

        // Display the name of the file that was selected.
        Text {
            id: fileText
            width: 200
            height: fileSelectButton.height
            verticalAlignment: Text.AlignVCenter
            text: "No File Selected"
            // If the text is too long to fit into the text box, display as much
            // of the RHS of the file name that can be displayed.
            elide: Text.ElideRight
        }
    }

    // The actual dialog that allows the user to select files.
    FileDialog {
        id: fileDialog
        selectMultiple: false
        selectExisting: false
        // When the user clicks OK to select the files...
        onAccepted: {
            // Get the absolute file path from the fileUrl property of this object.
            var urlString = fileUrl.toString();
            // JS code to get the filename from the absolute file path string.
            // QML supports embedded JS.
            var fileName = urlString.slice(urlString.lastIndexOf("/")+1,
            fileUrl.length);
            // Update the file name display.
            fileText.text = fileName
        }
    }
}
