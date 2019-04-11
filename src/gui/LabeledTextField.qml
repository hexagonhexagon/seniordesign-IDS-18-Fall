import QtQuick 2.12
import QtQuick.Controls 2.5

Row {
    spacing: 5
    property alias label: fieldLabel.text
    property alias text: field.text
    property alias field: field
    Label {
        id: fieldLabel
        height: field.height
        verticalAlignment: Text.AlignVCenter
    }
    TextField {
        id: field
        selectByMouse: true
    }
}
