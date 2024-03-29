

/*
 * Copyright (C) 2021  Aaron Hafer
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; version 3.
 *
 * gem is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */
import QtQuick 2.7
import Ubuntu.Components 1.3
//import QtQuick.Controls 2.2
import QtQuick.Layouts 1.3
import Qt.labs.settings 1.0
import io.thp.pyotherside 1.3
import Ubuntu.Components.Popups 1.3

MainView {
    applicationName: "gem.aaron"
    backgroundColor: "#515151"
    width: units.gu(45)
    height: units.gu(75)

    Page {
        id: root
        anchors.fill: parent

        header: PageHeader {
            id: pageHeader
            flickable: flick
            exposed: true

            leadingActionBar {
                numberOfSlots: 2
                actions: [
                    Action {
                        id: forward
                        iconName: "go-next"
                        visible: false

                        onTriggered: {
                            python.call('gemini.forward', [flick.contentY])
                        }

                        Component.onCompleted: {
                            python.setHandler('showForward', function () {
                                forward.visible = true
                            })

                            python.setHandler('hideForward', function () {
                                forward.visible = false
                            })
                        }
                    },
                    Action {
                        id: back
                        iconName: "go-previous"

                        onTriggered: {
                            python.call('gemini.back', [flick.contentY])
                        }
                    }
                ]
            }

            trailingActionBar {
                numberOfSlots: 2
                actions: [
                    Action {
                        id: reload
                        iconName: "reload"

                        onTriggered: {
                            python.call('gemini.reload',
                                        [adress.text, flick.contentY])
                        }
                    },
                    Action {
                        id: bookmark
                        iconName: "non-starred"
                        onTriggered: PopupUtils.open(dialog)
                    }
                ]
            }
            contents: TextField {
                id: adress
                text: "gemini://gemini.circumlunar.space/servers/"
                anchors {
                    fill: parent
                    margins: units.gu(1.5)
                }

                onActiveFocusChanged: {
                    if (activeFocus) {
                        back.visible = false
                    } else {
                        back.visible = true
                    }
                }
                Keys.onReturnPressed: {
                    python.call('gemini.goto', [adress.text, flick.contentY])
                }

                onAccepted: {
                    python.call('gemini.goto', [adress.text, flick.contentY])
                }
            }
        }
        Component {
            id: dialog
            Dialog {
                id: dialogue
                title: "Save Bookmark"
                TextField {
                    id: bmurl
                    text: adress.text
                    placeholderText: "url"
                    hasClearButton: true
                }
                TextField {
                    id: bmname
                    text: ""
                    placeholderText: "Name"
                    hasClearButton: true
                }
                Button {
                    text: "cancel"
                    onClicked: PopupUtils.close(dialogue)
                }
                Button {
                    text: "save"
                    color: UbuntuColors.orange
                    onClicked: {
                        forceActiveFocus()
                        python.call('bookmark.add', [bmurl.text, bmname.text])
                        python.call('bookmark.returnvalues', [false, true],
                                    function (names) {
                                        console.log(names)
                                        bottomEdge.repeaterModel = names
                                    })
                        PopupUtils.close(dialogue)
                    }
                }
            }
        }
        Flickable {
            id: flick
            anchors.margins: units.gu(1)
            anchors.fill: parent
            contentHeight: content.paintedHeight

            MouseArea {
                // This is to remove focus from the address bar when tapping off of it
                anchors.fill: parent
                onClicked: forceActiveFocus()
            }

            Text {
                anchors.fill: parent
                id: content
                width: root.width
                color: "#FFFFFFFF"
                textFormat: Text.RichText
                font.pointSize: units.gu(1.5)
                wrapMode: Text.WordWrap

                onLinkActivated: {
                    python.call('gemini.goto', [link, flick.contentY])
                }
            }
        }

        Component {
            id: inputComponent

            Dialog {
                id: inputDialog
                title: "Input requested"

                property bool isSecret: false

                function submit() {
                    forceActiveFocus()
                    python.call('gemini.handle_input', [inputfield.text])
                    PopupUtils.close(inputDialog)
                }

                TextField {
                    id: inputfield
                    hasClearButton: true
                    echoMode: isSecret ? TextInput.Password : TextInput.Normal

                    onAccepted: submit()
                }
                Button {
                    text: "cancel"
                    onClicked: PopupUtils.close(inputDialog)
                }
                Button {
                    text: "send"
                    color: UbuntuColors.orange
                    onClicked: submit()
                }
            }
        }

        BottomEdge {
            id: bottomEdge
            property var repeaterModel: [] //I need to propagate using this property because I cant acces loaded Components directly
            clip: true
            height: parent.height
            hint {
                text: "Bookmarks"
            }
            contentComponent: Rectangle {
                clip: true
                width: bottomEdge.width
                height: bottomEdge.height
                color: "#515151"
                Rectangle {
                    z: 1
                    color: "black"
                    height: bmToolbar.height
                    width: parent.width
                    Toolbar {
                        id: bmToolbar
                        anchors.left: parent.left
                        anchors.top: parent.top
                        anchors.topMargin: parent.height / 2 - bmToolbar.height / 2
                        anchors.leftMargin: 15
                        leadingActionBar.actions: [
                            Action {
                                iconName: "down"
                                text: "Collapse"
                                onTriggered: bottomEdge.collapse()
                            }
                        ]
                    }
                }
                Flickable {
                    id: bmFlick
                    width: parent.width
                    height: parent.height - bmToolbar.height * 2
                    anchors.top: bmToolbar.bottom
                    contentHeight: bmClm.implicitHeight
                    Column {
                        id: bmClm
                        anchors.fill: parent
                        anchors.topMargin: 100
                        Repeater {
                            id: repeater
                            model: bottomEdge.repeaterModel
                            ListItem {
                                color: "#515151"
                                highlightColor: "white"
                                Text {
                                    id: bmText
                                    anchors.centerIn: parent
                                    color: "#FFFFFFFF"
                                    font.pointSize: 35
                                    wrapMode: Text.WordWrap
                                    text: modelData
                                }
                                onClicked: {
                                    python.call('bookmark.allocate',
                                                [modelData], function (url) {
                                                    console.log(url)
                                                    python.call('gemini.goto',
                                                                [url, flick.contentY])
                                                })
                                    bottomEdge.collapse()
                                }
                                leadingActions: ListItemActions {
                                    actions: [
                                        Action {
                                            iconName: "delete"
                                            onTriggered: {
                                                python.call('bookmark.allocate',
                                                            [modelData],
                                                            function (url) {
                                                                console.log("allocate")
                                                                console.log(url)
                                                                console.log(modelData)
                                                                console.log("allocatestop")
                                                                python.call('bookmark.remove',
                                                                            [url, modelData])
                                                                python.call('bookmark.returnvalues',
                                                                            [false, true],
                                                                            function (names) {
                                                                                console.log(names)
                                                                                bottomEdge.repeaterModel = names
                                                                            })
                                                            })
                                            }
                                        }
                                    ]
                                }
                            }
                        }
                    }
                }
            }
        }

        Python {
            id: python

            Component.onCompleted: {
                addImportPath(Qt.resolvedUrl('../src/'))

                importNames('gemini', ['gemini'], function () {
                    console.log('module gemini imported')

                    python.setHandler('loading', function (url) {
                        content.text = "<center>Loading.. Stay calm!</center> <br> <center>(っ⌒‿⌒)っ</center>"
                        adress.text = url
                    })

                    python.setHandler('onLoad',
                                      function (gemsite, scrollHeight) {
                                          content.text = gemsite

                                          if (scrollHeight) {
                                              flick.contentY = scrollHeight
                                          }
                                      })

                    python.setHandler('externalUrl', function (url) {
                        Qt.openUrlExternally(url)
                    })

                    python.setHandler('requestInput',
                                      function (message, isSecret) {
                                          PopupUtils.open(inputComponent, null,
                                                          {
                                                              "text": message,
                                                              "isSecret": isSecret
                                                          })
                                      })

                    python.call('gemini.load_initial_page')
                })
                importNames('bookmarks', ['bookmark'], function () {
                    console.log('module bookmark imported')

                    python.call('bookmark.returnvalues', [false, true],
                                function (names) {
                                    console.log(names)
                                    bottomEdge.repeaterModel = names
                                })
                })
            }

            onError: {
                console.log('python error: ' + traceback)
            }
        }
    }
}
