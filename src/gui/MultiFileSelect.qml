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
    property alias fileUrls: fileDialog.fileUrls

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

        // A ListView allows a list of things to be displayed. See
        // https://qmlbook.github.io/ch07-modelview/modelview.html for a good
        // explanation.
        ListView {
            id: fileDisplay
            spacing: 5
            width: 100
            // The ListView is always made tall enough to be able to show all
            // files selected at once.
            height: contentHeight
            // The list of things we are displaying is in the
            // fileSelectionModel, which contains all the details of what we want
            // to display.
            model: fileSelectionModel
            // How to display each item in the model is given by the delegate,
            // which takes info about the item in the model and displays it in a
            // special manner.
            delegate: fileDelegate
        }
    }

    // A ListModel is a model that can be passed into the ListView to tell it
    // what to display. Each list element has a fileName attribute.
    ListModel {
        id: fileSelectionModel
        ListElement { fileName: "No File Selected" }
    }

    // The delegate that displays a list element properly, using the fileName
    // attribute the ListView will pass in automatically.
    Component {
        id: fileDelegate
        Text {
            width: 200
            text: fileName
            elide: Text.ElideRight
        }
    }

    // The actual dialog that allows the user to select files.
    FileDialog {
        id: fileDialog
        // Setting this to true allows the user to select multiple files; this
        // is false by default.
        selectMultiple: true
        // When the user clicks OK to choose the files...
        onAccepted: {
            // Clear all files currently stored in the ListModel.
            fileSelectionModel.clear()
            // Iterate through the list of files selected by using the fileUrls
            // property of this object.
            for (var i = 0; i < fileUrls.length; i++) {
                // For each URL in fileUrls, get the file name from the URL.
                var urlString = fileUrls[i].toString();
                var fileName = urlString.slice(urlString.lastIndexOf("/")+1, fileUrl.length);
                // Add the file name to the ListModel. The ListView will
                // automatically update.
                fileSelectionModel.append({"fileName": fileName})
            }
        }
    }
}
