import QtQuick 1.0

Rectangle {
    height:400
    width:50
    color:"transparent"
    
    Rectangle {
        id: fullbattery
        height:300
        width:40
        anchors.centerIn:parent
        border.width:2
        border.color:"green"
        Column {
            anchors.bottom:parent.bottom
            spacing:1
            Repeater {

                model: 5
                id: battery
                
                Rectangle {
                    width: fullbattery.width
                    height:fullbattery.height/5
                    color:"green"
                    
                }
            }
        }
    }
}
