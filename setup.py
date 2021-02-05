from distutils.core import setup
import py2exe

setup(windows=[
    {
        "script": "blackjackclient.py",
        "icon_resources": [(1, "chip.ico")],
        "dest_base" : "Dumfing's Blackjack"
    }
],
    data_files=[('', ['1_chip.png'])],
    options={
        'py2exe': {
            'bundle_files': 1,
            'compressed': True,
            'optimize': 2,
        }},
    zipfile=None,

)
