import os


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
    return create_selenium_container_chrome()


def create_selenium_container_chrome():
    import os
    
    commands = [
        "docker",
        "run -d",
        "-p 4445:4444",
        "-p 5913:5900",
        "--name bbsel",
        "-v ${HOME}/Downloads/docker/:/home/seluser/Downloads/",
        "selenium/standalone-chrome",
    ]
    # '  '.join(commands)
    stream_docker = os.popen(' '.join(commands))
    docker_ff_id = stream_docker.read().rstrip()

    print('Started docker with id '+docker_ff_id)
    return docker_ff_id


def create_selenium_container_ff():
    commands = [
        "docker",
        "run -d",
        "-p 4445:4444",
        "-p 5913:5900",
        "--name bbsel",
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


def start_driver_ff():
    import sys
    sys.path.append('/python')
    import selenium_utilities
    from selenium import webdriver
    import time

    # start a selenium container
    docker_ff_id = selenium_utilities.start_selenium()
    time.sleep(5)

    profile = webdriver.FirefoxProfile()
    profile.set_preference("browser.preferences.instantApply", True)
    profile.set_preference('browser.safebrowsing.downloads.enabled', False)
    profile.set_preference('browser.download.panel.shown', False)
    profile.set_preference('browser.download.manager.closeWhenDone', True)
    profile.set_preference("browser.helperApps.neverAsk.saveToDisk",
                           'text/plain, application/octet-stream, application/binary, text/csv, application/csv, '
                           'text/CSV, application/CSV, text/comma-separated-values, application/excel, '
                           'application/download, text/xml, application/xml')
    profile.set_preference('browser.helperApps.alwaysAsk.force', False)
    profile.set_preference('dom.disable_open_during_load', False)
    profile.set_preference('dom.disable_beforeunload', True)
    profile.set_preference('dom.file.createInChild', True)

    driver = webdriver.Remote(
        "http://127.0.0.1:4445/wd/hub",
        desired_capabilities=webdriver.DesiredCapabilities.FIREFOX,
        browser_profile=profile
        )
    return driver



def start_driver_chrome():
    import sys
    sys.path.append('/python')
    import selenium_utilities
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    import time

    # start a selenium container
    docker_ff_id = selenium_utilities.start_selenium()
    time.sleep(5)

    chrome_options = webdriver.ChromeOptions()
    chrome_options.set_headless = True
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-logging')
    chrome_options.add_argument('--start-maximized') # open Browser in maximized mode
    chrome_options.add_argument('--disable-infobars') # disabling infobars
    chrome_options.add_argument('--disable-dev-shm-usage') # overcome limited resource problems
    chrome_options.add_argument('--disable-setuid-sandbox')
    chrome_options.add_argument('--disable-extensions')

    driver = webdriver.Remote(
        command_executor="http://127.0.0.1:4445/wd/hub",
        options=chrome_options
    )

    driver = webdriver.Remote(
        command_executor="http://127.0.0.1:4445/wd/hub",
        desired_capabilities=chrome_options.to_capabilities()
    )
    return driver
    driver.close()


def start_driver_local_chrome():
    from selenium import webdriver
    chrome_options = webdriver.ChromeOptions()
    #chrome_options.add_argument('--headless')
    prefs = {"profile.default_content_settings.popups": 0,
                "download.default_directory": r"/Users/andrewfelton/Downloads/docker/",
                "directory_upgrade": True}
    chrome_options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(desired_capabilities=chrome_options.to_capabilities())
    return driver


def start_driver():
    return start_driver_local_chrome()


