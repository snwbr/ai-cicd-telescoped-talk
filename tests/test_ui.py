from app.ui import button_label

def test_ui_button_label_caps():
    assert button_label("click") == "CLICK"
