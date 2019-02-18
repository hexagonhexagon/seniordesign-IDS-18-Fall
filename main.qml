import QtQuick 2.0
import QtQuick.Window 2.0
import QtQuick.Controls 2.0

Window
{
    visible: true
    width: 843
    height: 528
    title: qsTr("IDS GUI")

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

    Image
    {
        id: background
        anchors.fill: parent
        fillMode: Image.Stretch
        source: "IDS_GUI_Assets/Background.png"

        Image
        {
            id: fuelGauge
            x: 447
            y: 67
            width: 277
            height: 198
            fillMode: Image.PreserveAspectFit
            source: "IDS_GUI_Assets/fuelGauge.png"

            Image
            {
                id: fuelSupport
                x: 123
                y: 83
                width: 44
                height: 33
                fillMode: Image.PreserveAspectFit
                source: "IDS_GUI_Assets/supportSmall.png"
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
            source: "IDS_GUI_Assets/tempGauge.png"

            Image {
                id: tempSupport
                x: 97
                y: 64
                width: 44
                height: 33
                fillMode: Image.PreserveAspectFit
                source: "IDS_GUI_Assets/supportSmall.png"
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
        source: "IDS_GUI_Assets/BackgroundLights.png"

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
            source: "IDS_GUI_Assets/OilLight.png"
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
            source: "IDS_GUI_Assets/BatteryLight.png"
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
            source: "IDS_GUI_Assets/FluidLight.png"
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
            source: "IDS_GUI_Assets/LowbeamLight.png"
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
            source: "IDS_GUI_Assets/SeatbeltLight.png"
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
            source: "IDS_GUI_Assets/EngineLight.png"
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
            source: "IDS_GUI_Assets/AirbagLight.png"
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
            source: "IDS_GUI_Assets/HighbeamLight.png"
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
            source: "IDS_GUI_Assets/TempLight.png"
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
            source: "IDS_GUI_Assets/ABSLight.png"
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
            source: "IDS_GUI_Assets/ParkingBrakeLight.png"
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
            source: "IDS_GUI_Assets/TractionLight.png"
        }

        Image
        {
            id: oilOff
            x: 109
            y: 96
            width: 49
            height: 41
            fillMode: Image.PreserveAspectFit
            source: "IDS_GUI_Assets/OilOff.png"
        }

        Image
        {
            id: batteryOff
            x: 177
            y: 96
            width: 50
            height: 41
            fillMode: Image.PreserveAspectFit
            source: "IDS_GUI_Assets/BatteryOff.png"
        }

        Image
        {
            id: fluidOff
            x: 235
            y: 96
            width: 55
            height: 41
            fillMode: Image.PreserveAspectFit
            source: "IDS_GUI_Assets/FluidOff.png"
        }

        Image
        {
            id: highbeamOff
            x: 300
            y: 88
            width: 48
            height: 49
            fillMode: Image.PreserveAspectFit
            source: "IDS_GUI_Assets/HighbeamOff.png"
        }

        Image
        {
            id: seatbeltOff
            x: 108
            y: 145
            width: 52
            height: 45
            fillMode: Image.PreserveAspectFit
            source: "IDS_GUI_Assets/SeatbeltOff.png"
        }

        Image
        {
            id: engineOff
            x: 174
            y: 143
            width: 55
            height: 49
            fillMode: Image.PreserveAspectFit
            source: "IDS_GUI_Assets/EngineOff.png"
        }

        Image
        {
            id: airbagOff
            x: 235
            y: 147
            width: 55
            height: 41
            fillMode: Image.PreserveAspectFit
            source: "IDS_GUI_Assets/AirbagOff.png"
        }

        Image
        {
            id: lowbeamOff
            x: 298
            y: 151
            width: 52
            height: 41
            fillMode: Image.PreserveAspectFit
            source: "IDS_GUI_Assets/LowbeamOff.png"
        }

        Image
        {
            id: tempOff
            x: 106
            y: 208
            width: 55
            height: 49
            fillMode: Image.PreserveAspectFit
            source: "IDS_GUI_Assets/TempOff.png"
        }

        Image
        {
            id: absOff
            x: 174
            y: 208
            width: 55
            height: 49
            fillMode: Image.PreserveAspectFit
            source: "IDS_GUI_Assets/ABSOff.png"
        }

        Image
        {
            id: parkingBrakeOff
            x: 235
            y: 208
            width: 55
            height: 49
            fillMode: Image.PreserveAspectFit
            source: "IDS_GUI_Assets/ParkingBrakeOff.png"
        }

        Image
        {
            id: tractionOff
            x: 296
            y: 208
            width: 55
            height: 49
            fillMode: Image.PreserveAspectFit
            source: "IDS_GUI_Assets/TractionOff.png"
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
        source: "IDS_GUI_Assets/Speedometer.png"


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
            source: "IDS_GUI_Assets/NeedleLarge.png"
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
            source: "IDS_GUI_Assets/SupportLarge.png"
        }
    }


    Button
    {
        id: decreaseSpeed
        x: 47
        y: 417
        width: 39
        height: 42
        text: qsTr("-")
        onClicked: (speedometerRotationAngle <= -136) ? speedometerRotationAngle = -136 : speedometerRotationAngle -=1;
    }

    Button
    {
        id: increaseSpeed
        x: 202
        y: 417
        width: 39
        height: 42
        text: qsTr("+")
        focusPolicy: Qt.WheelFocus
        onClicked: (speedometerRotationAngle >= 150) ? speedometerRotationAngle = 150 : speedometerRotationAngle +=1;
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
            source: "IDS_GUI_Assets/NeedleLarge.png"
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
            source: "IDS_GUI_Assets/SupportLarge.png"
        }

        source: "IDS_GUI_Assets/Tachometer.png"
        rotation: 0
    }

    Button
    {
        id: turnOilLightOn
        x: 305
        y: 427
        width: 32
        height: 23
        text: qsTr("Oil")
        display: AbstractButton.IconOnly
        focusPolicy: Qt.WheelFocus
        onClicked: (oilLightOn) ? oilLightOn = false : oilLightOn = true;
    }

    Button
    {
        id: turnBatteryLightOn
        x: 371
        y: 427
        width: 32
        height: 23
        text: qsTr("Battery")
        font.pointSize: 8
        display: AbstractButton.IconOnly
        focusPolicy: Qt.WheelFocus
        onClicked: (batteryLightOn) ? batteryLightOn = false : batteryLightOn = true;
    }

    Button
    {
        id: turnFluidLightOn
        x: 434
        y: 427
        width: 32
        height: 23
        text: qsTr("Oil")
        display: AbstractButton.IconOnly
        focusPolicy: Qt.WheelFocus
        onClicked: (fluidLightOn) ? fluidLightOn = false : fluidLightOn = true;
    }

    Button
    {
        id: turnHighBeamLightOn
        x: 493
        y: 427
        width: 32
        height: 23
        text: qsTr("Oil")
        display: AbstractButton.IconOnly
        focusPolicy: Qt.WheelFocus
        onClicked: (highBeamLightOn) ? highBeamLightOn = false : highBeamLightOn = true;
    }

    Button
    {
        id: turnSeatbeltLightOn
        x: 305
        y: 461
        width: 32
        height: 23
        text: qsTr("Oil")
        display: AbstractButton.IconOnly
        focusPolicy: Qt.WheelFocus
        onClicked: (seatBeltLightOn) ? seatBeltLightOn = false : seatBeltLightOn = true;
    }


    Button
    {
        id: turnEngineLightOn
        x: 371
        y: 461
        width: 32
        height: 23
        text: qsTr("Oil")
        display: AbstractButton.IconOnly
        focusPolicy: Qt.WheelFocus
        onClicked: (engineLightOn) ? engineLightOn = false : engineLightOn = true;
    }

    Button
    {
        id: turnAirbagLightOn
        x: 434
        y: 461
        width: 32
        height: 23
        text: qsTr("Oil")
        display: AbstractButton.IconOnly
        focusPolicy: Qt.WheelFocus
        onClicked: (airbagLightOn) ? airbagLightOn = false : airbagLightOn = true;
    }

    Button
    {
        id: turnLowbeamLightOn
        x: 493
        y: 461
        width: 32
        height: 23
        text: qsTr("Oil")
        display: AbstractButton.IconOnly
        focusPolicy: Qt.WheelFocus
        onClicked: (lowBeamLightOn) ? lowBeamLightOn = false : lowBeamLightOn = true;
    }

    Button
    {
        id: turnTempLightOn
        x: 305
        y: 490
        width: 32
        height: 23
        text: qsTr("Oil")
        display: AbstractButton.IconOnly
        focusPolicy: Qt.WheelFocus
        onClicked: (tempLightOn) ? tempLightOn = false : tempLightOn = true;
    }

    Button
    {
        id: turnABSLightOn
        x: 371
        y: 491
        width: 32
        height: 23
        text: qsTr("Oil")
        display: AbstractButton.IconOnly
        focusPolicy: Qt.WheelFocus
        onClicked: (absLightOn) ? absLightOn = false : absLightOn = true;
    }

    Button
    {
        id: turnBrakeLightOn
        x: 434
        y: 491
        width: 32
        height: 22
        text: qsTr("Oil")
        display: AbstractButton.IconOnly
        focusPolicy: Qt.WheelFocus
        onClicked: (brakeLightOn) ? brakeLightOn = false : brakeLightOn = true;
    }

    Button
    {
        id: turnTractionLightOn
        x: 493
        y: 490
        width: 32
        height: 23
        text: qsTr("Oil")
        display: AbstractButton.IconOnly
        focusPolicy: Qt.WheelFocus
        onClicked: (tractionLightOn) ? tractionLightOn = false : tractionLightOn = true;
    }

    Button
    {
        id: increaseRPM
        x: 752
        y: 417
        width: 39
        height: 42
        text: qsTr("+")
        focusPolicy: Qt.WheelFocus
        onClicked: (tachometerRotationAngle >= 103) ? tachometerRotationAngle = 103 : tachometerRotationAngle +=10;
    }

    Button
    {
        id: decreaseRPM
        x: 630
        y: 417
        width: 39
        height: 42
        text: qsTr("-")
        onClicked: (tachometerRotationAngle <= -103) ? tachometerRotationAngle = -103 : tachometerRotationAngle -=10;
    }

    Image
    {
        id: turnBackground
        x: 117
        y: 11
        width: 609
        height: 298
        fillMode: Image.PreserveAspectFit
        source: "IDS_GUI_Assets/turnBackground.png"

        Image
        {
            id: turnLeftOff
            x: 240
            y: 121
            width: 52
            height: 56
            fillMode: Image.PreserveAspectFit
            source: "IDS_GUI_Assets/turnLeftOff.png"
        }

        Image
        {
            id: turnRightOff
            x: 321
            y: 119
            width: 53
            height: 60
            fillMode: Image.PreserveAspectFit
            source: "IDS_GUI_Assets/turnRightOff.png"
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
            source: "IDS_GUI_Assets/turnLeftLight.png"
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
            source: "IDS_GUI_Assets/turnRightLight.png"
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

        Button
        {
            id: turnLeftLightOn
            x: 240
            y: 57
            width: 37
            height: 40
            text: qsTr("Button")
            display: AbstractButton.IconOnly
            onClicked:
            {
                rightTurnLightActivated = false;
                hazardsActivated = false;
                turnRightOn.visible = false;
                (leftTurnLightActivated) ? leftTurnLightActivated = false : leftTurnLightActivated = true;

                if(leftTurnLightActivated)
                    leftTurnLightOn = true

                else
                    leftTurnLightOn = false

                turnLeftOn.visible = leftTurnLightOn
            }
        }

        Button
        {
            id: turnRightLightOn
            x: 329
            y: 57
            width: 37
            height: 40
            text: qsTr("Button")
            display: AbstractButton.IconOnly
            onClicked:
            {
                leftTurnLightActivated = false;
                hazardsActivated = false;
                turnLeftOn.visible = false;
                (rightTurnLightActivated) ? rightTurnLightActivated = false : rightTurnLightActivated = true;

                if(rightTurnLightActivated)
                    rightTurnLightOn = true

                else
                    rightTurnLightOn = false

                turnRightOn.visible = rightTurnLightOn
            }
        }

        Button
        {
            id: turnHazardsOn
            x: 286
            y: 205
            width: 37
            height: 18
            text: qsTr("Button")
            display: AbstractButton.IconOnly
            onClicked:
            {
                leftTurnLightActivated = false;
                rightTurnLightActivated = false;

                (hazardsActivated) ? hazardsActivated = false : hazardsActivated = true;

                if(hazardsActivated)
                {
                    rightTurnLightOn = true
                    leftTurnLightOn = true
                }

                else
                {
                    rightTurnLightOn = false
                    leftTurnLightOn = false
                }

                turnRightOn.visible = rightTurnLightOn
                turnLeftOn.visible = leftTurnLightOn
            }
        }
    }



}
