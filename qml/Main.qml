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
//import Ubuntu.Components 1.3
//import QtQuick.Controls 2.2
import QtQuick.Layouts 1.3
import Qt.labs.settings 1.0
import io.thp.pyotherside 1.3

 Rectangle{
    id: root


    width: 1080
    height: 1920
    Rectangle {
      id: searchbar
      color: "grey"
      z: 1
      height: root.height / 12
      anchors.left: parent.left
      anchors.top: parent.top
      anchors.right: parent.right
      Rectangle{
        color: "white"
        anchors.fill: parent
        anchors.centerIn: parent
        anchors.topMargin: 1/5 * parent.height
        anchors.bottomMargin: 1/5 * parent.height
        anchors.leftMargin: 1/5 * parent.height
        anchors.rightMargin: 1/5 * parent.height
        TextInput{
          id: adress
          anchors.fill: parent
          anchors.topMargin: parent.height / 3
          anchors.leftMargin: 1/5 * parent.height
          anchors.centerIn: parent
          font.pointSize: 20
          text: "gemini://gemini.circumlunar.space/servers/"


        }
        Rectangle{
          width: adress.height
          height: adress.height

          anchors.right: parent.right
          anchors.rightMargin: 1/5 * parent.height
          anchors.verticalCenter: parent.verticalCenter


          Image{
            source: "../assets/search.png"
            anchors.fill: parent
            anchors.centerIn: parent

          }
          MouseArea {
              anchors.fill: parent
              onReleased: {
                python.call('gemini.main', [adress.text], function(returnValue) {
                    content.text = returnValue;
                })
              }
          }
        }
      }
    }
    Flickable {
        id: flick
        anchors.left: parent.left
        anchors.top: searchbar.bottom
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        contentHeight: content.paintedHeight
        Text{
          id: content
          width: root.width

          textFormat : Text.RichText
          font.pointSize: 20
          minimumPointSize: 10
          fontSizeMode: Text.HorizontalFit
          wrapMode: Text.WordWrap

          onLinkActivated: {
            python.call('gemini.main', [link], function(returnValue) {
                content.text = returnValue;
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
                    content.text = returnValue;
                })
            });
        }

        onError: {
            console.log('python error: ' + traceback);
        }
    }
}
