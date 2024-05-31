import pytest

from unittest.mock import patch
from pytestqt.qtbot import QtBot
from PyQt5.QtWidgets import QStackedWidget, QMessageBox
from widgets.main_window import MainWindow

# for creating class
@pytest.fixture
def widget(qtbot):
    widget = MainWindow(QStackedWidget())
    qtbot.addWidget(widget)
    return widget

# for basic app
def test_change_theme(widget):
    initial_theme = widget.light_theme
    widget.change_theme()
    assert widget.light_theme == (not initial_theme)

def test_show_message(widget, qtbot):
    with patch.object(QMessageBox, 'about') as mock_about:
        widget.show_message()
        mock_about.assert_called_once_with(widget, "Message", "Added to favorites ❤ ")

def test_play_audio(widget):
    with patch.object(widget.player, 'play') as mock_play:
        widget.play_audio()
        mock_play.assert_called_once()

def test_pause_audio(widget):
    with patch.object(widget.player, 'pause') as mock_pause:
        widget.pause_audio()
        mock_pause.assert_called_once()

def test_change_volume(widget):
    new_volume = 50
    with patch.object(widget.player, 'setVolume') as mock_set_volume:
        widget.change_volume(new_volume)
        mock_set_volume.assert_called_once_with(new_volume)

def test_next_m(widget):
    initial_index = widget.current_index
    widget.next_m()
    assert widget.current_index == (initial_index + 1) % len(widget.tracks)
    assert widget.playlist_index[widget.current_playlist] == widget.current_index

def test_prev_m(widget):
    initial_index = widget.current_index
    widget.prev_m()
    assert widget.current_index == (initial_index - 1) % len(widget.tracks)
    assert widget.playlist_index[widget.current_playlist] == widget.current_index