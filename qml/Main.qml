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

MainView {
  applicationName: "Gem"
  backgroundColor: "#515151"

  Page {
      id: root

      header: PageHeader {
        id: pageHeader
        flickable: flick
        exposed: true
        leadingActionBar {
          numberOfSlots: 1
          actions: [
            Action {
              id: back
              iconName: "back"
              onTriggered: {
                content.text = "<center>Loading.. Stay calm!</center> <br> <center>(っ⌒‿⌒)っ</center>"
                python.call('gemini.back', [], function(returnValue) {
                    adress.text = returnValue;
                    python.call('gemini.main', [adress.text], function(returnValue) {
                        console.assert(returnValue.status === 'success', returnValue.message);
                        content.text = returnValue.content;
                    })
                })
              }
            }
          ]
        }

        contents: Rectangle {
          id: addressWrapper
          radius: 15
          color: "#F0F0F0"
          anchors.fill: parent
          anchors.topMargin: 15
          anchors.bottomMargin: 15

          TextInput {
            id: adress
            anchors {
              fill: parent
              centerIn: parent
              leftMargin: 10
              rightMargin: 10
            }
            verticalAlignment: Qt.AlignVCenter
            horizontalAlignment: Qt.AlignLeft
            text: "gemini://gemini.circumlunar.space/servers/"

            onActiveFocusChanged: {
              if (activeFocus) {
                back.visible = false
              } else {
                back.visible = true
              }
            }

            onAccepted: {
              content.text = "<center>Loading.. Stay calm!</center> <br> <center>(っ⌒‿⌒)っ</center>"
              python.call('gemini.main', [adress.text], function(returnValue) {
                  console.assert(returnValue.status === 'success', returnValue.message);
                  content.text = returnValue.content;
              })
              python.call('gemini.history', [adress.text], function(returnValue) {
                  console.log("");
              })
              python.call('gemini.where_am_I', ["forward"], function(returnValue) {
                  console.log("");
              })
            }
          }
        }
      }
      
      Flickable {
        id: flick
        anchors.fill: parent
        contentHeight: content.paintedHeight

        Text{
          id: content
          width: root.width
          color: "#FFFFFFFF"
          textFormat : Text.RichText
          font.pointSize: 35
          wrapMode: Text.WordWrap
          onLinkActivated: {
            content.text = "<center>Loading.. Stay calm!</center> <br> <center>(っ⌒‿⌒)っ</center>"
            python.call('gemini.history', [link], function(returnValue) {})
            python.call('gemini.where_am_I', ["forward"], function(returnValue) {})
            python.call('gemini.main', [link], function(returnValue) {
                console.assert(returnValue.status === 'success', returnValue.message);

                content.text = returnValue.content;
                adress.text = link
            })
          }
        }
      }

      Python {
          id: python

          Component.onCompleted: {
              addImportPath(Qt.resolvedUrl('../src/'));

              importModule('gemini', function() {
                  console.log('module imported');
                  python.call('gemini.main', ['gemini://gemini.circumlunar.space/servers/'], function(returnValue) {
                      console.assert(returnValue.status === 'success', returnValue.message);

                      content.text = returnValue.content;
                  })
                  python.call('gemini.where_am_I', ['forward'], function(returnValue) {})
                  python.call('gemini.history', ['gemini://gemini.circumlunar.space/servers/'], function(returnValue) {})
              });
          }

          onError: {
              console.log('python error: ' + traceback);
          }
      }
  }
}
