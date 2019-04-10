import QtQuick 2.12
import QtQuick.Controls 2.5

Row {
    id: root
    spacing: 5
    property alias label: sliderLabel.text
    property alias value: slider.value
    // Alias for the Slider.moved signal. Since the slider inside cannot be
    // accessed when this is used elsewhere, it needs to be passed here in order to
    // be able to be intercepted.
    signal moved

    Label {
        id: sliderLabel
        width: 110
        horizontalAlignment: Text.AlignRight
        // The text box is the tallest object in the row, so we set this
        // object's height to the text box's and center it vertically to get it
        // to look good.
        height: sliderValueField.height
        verticalAlignment: Text.AlignVCenter
    }

    Slider {
        id: slider
        // Minimum step you can move the slider by.
        stepSize: 0.005
        width: 100
        height: sliderValueField.height
        // Pass this object's moved signal to the root object.
        onMoved: root.moved()
    }

    TextField {
        id: sliderValueField
        width: 60
        // The maximum number of characters the box can have.
        maximumLength: 5
        // Always display 3 decimal places of the current float value, rounded.
        text: slider.value.toFixed(3)
        // Allow the user to highlight text inside the box.
        selectByMouse: true
        // Enforce that the input must be a float.
        validator: DoubleValidator {
            bottom: 0.0
            top: 1.0
        }
        // When the box is deselected or the user presses Enter, update the
        // slider value and emit the moved signal so any updates that that might
        // cause actually happen.
        onAccepted: {
            slider.value = text
            slider.moved()
        }
    }
}
