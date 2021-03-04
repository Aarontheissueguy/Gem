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

 Rectangle{
    id: root
    color: "#515151"

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
      radius: 3
      Rectangle{
        color: "white"
        anchors.fill: parent
        anchors.centerIn: parent
        anchors.topMargin: 1/5 * parent.height
        anchors.bottomMargin: 1/5 * parent.height
        anchors.leftMargin: 1/5 * parent.height
        anchors.rightMargin: 1/5 * parent.height
        radius: 15
        TextInput{
          id: adress
          anchors.fill: parent
          anchors.topMargin: parent.height / 3
          anchors.leftMargin: 1/5 * parent.height
          anchors.centerIn: parent
          text: "gemini://gemini.circumlunar.space/servers/"


        }
        Rectangle{
          id: searchRec
          width: adress.height
          height: adress.height

          anchors.right: parent.right
          anchors.rightMargin: 1/5 * parent.height
          anchors.verticalCenter: parent.verticalCenter


          Image{
            id: search
            source: "../assets/search.png"
            anchors.fill: parent
            anchors.centerIn: parent

          }
          MouseArea {
              anchors.fill: parent
              onPressed: {
                search.scale = 0.8
              }
              onReleased: {
                content.text = "<center>Loading.. Stay calm!</center> <br> <center>(っ⌒‿⌒)っ</center>"
                python.call('gemini.main', [adress.text], function(returnValue) {
                    content.text = returnValue;
                })
                python.call('gemini.history', [adress.text], function(returnValue) {
                    console.log("");
                })
                python.call('gemini.where_am_I', ["forward"], function(returnValue) {
                    console.log("");
                })
                search.scale = 1
              }
          }
        }
        Rectangle{
          width: adress.height
          height: adress.height

          anchors.right: searchRec.left
          anchors.rightMargin: 1/5 * parent.height
          anchors.verticalCenter: parent.verticalCenter


          Image{
            id: back
            source: "../assets/arrow.png"
            anchors.fill: parent
            anchors.centerIn: parent

          }
          MouseArea {
              anchors.fill: parent
              onPressed: {
                back.scale = 0.8
              }
              onReleased: {
                content.text = "<center>Loading.. Stay calm!</center> <br> <center>(っ⌒‿⌒)っ</center>"
                python.call('gemini.back', [], function(returnValue) {
                    adress.text = returnValue;
                    python.call('gemini.main', [adress.text], function(returnValue) {
                        content.text = returnValue;
                    })
                })
                back.scale = 1
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
