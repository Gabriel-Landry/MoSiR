"""
Copyright (c) 2023 Gouvernement du Québec
SPDX-License-Identifier: LiLiQ-R-1.1
License-Filename: LICENSES/EN/LiLiQ-R11unicode.txt
"""
import sys
sys.path.append("../MoSiR")

from MoSiR import Flaskwrapper
from MoSiR.blueprints.Mirowrapper.miro import Mirowrapper


if __name__ == '__main__':
    base_url = "http://localhost"
    port = 3000
    host = '0.0.0.0'
    server = Flaskwrapper(base_url,host,port)
    server.register(Mirowrapper())
    server.sign_in()
    server.run()
    
    

    