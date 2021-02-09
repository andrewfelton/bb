import os
import selenium

def start_selenium():
    commands = [
        "docker",
        "start",
        "bbsel"
    ]
    command = ' '.join(commands)
    stream_docker = os.popen(command)
    docker_ff_id = stream_docker.read().rstrip()

    print('Started docker with id '+docker_ff_id)
    return docker_ff_id


def create_selenium_container():
    commands = [
        "docker",
        "run -d",
        "-p 4445:4444",
        "-p 5913:5900",
        "--name bbsel"
        "-v ${HOME}/Downloads/docker/:/home/seluser/Downloads/",
    #    "selenium/standalone-firefox",
        "selenium/standalone-firefox-debug",
    ]
    ' '.join(commands)

    stream_docker = os.popen(' '.join(commands))
    docker_ff_id = stream_docker.read().rstrip()

    print('Started docker with id '+docker_ff_id)
    return docker_ff_id

def stop_selenium(docker_id):
    os.system('docker stop ' + docker_id)
    #os.system('docker rm ' + docker_id)


def start_driver():
    import os
    from datetime import date
    import sys
    sys.path.append('/Users/andrewfelton/Documents/bb/2021/python')
    import selenium_utilities
    import selenium
    from selenium import webdriver
    from selenium.webdriver.common.keys import Keys
    import time

    # start a selenium container
    docker_ff_id = selenium_utilities.start_selenium()
    time.sleep(5)

    profile = webdriver.FirefoxProfile()
    profile.set_preference('browser.download.manager.showWhenStarting', False)
    profile.set_preference('browser.download.manager.closeWhenDone', True)
    profile.set_preference('browser.helperApps.neverAsk.saveToDisk', ('text/csv,text/plain,application/octet-stream,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'))

    driver = webdriver.Remote(
        "http://127.0.0.1:4445/wd/hub", 
        desired_capabilities=webdriver.DesiredCapabilities.FIREFOX,
        browser_profile=profile
        )
    return driver

