"""
This file is used to generate a list of prompts for a given theme and then uses selenium 
to download the images
"""

import ast
import datetime
import random
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from dotenv import load_dotenv
import poe
import os
from string import Template
import shutil
import os
import os
from pathlib import Path
from dotenv import load_dotenv
import shutil
import ffmpeg
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
from selenium.webdriver.support.wait import WebDriverWait
import whisper
from threading import Thread
from urllib.request import urlopen
from ffprobe import FFProbe
load_dotenv()

cookie = os.getenv("POE_COOKIE")
client = poe.Client(cookie)




# this is changed
# create an enumerations for the modes



settings = {
    "video": {
        "prompts": 10,
        "width": 432,
        "height": 768,
        "duration": 30,
        "iterations": 24,
        "slowness": 1.25,
        "upscale": 1.5,
        "mode": "Zoom-in"
    },
    "voice": {
        "speaker": "p345",
        "intro": "Welcome to NeoClipse. The AI that creates videos from your imagination. Today we are going to create a video about",
        "outro": "Thank you for watching this video, if you enjoyed it please like and subscribe and I will see you in the next video."
    },
    "browser": {
        "headless": False,
    }
}

def generate_generic_prompt(message, model="a2"):
    try:
        response = ""
        for chunk in client.send_message(model, message, with_chat_break=True):
            response += chunk["text_new"]
        return response
    except:
        generate_generic_prompt(message, model)
    
def generate_video_prompts(topic,path):
    """
    Generates a list of prompts for a given theme
    :param theme: the theme to generate prompts for
    :param length: the number of prompts to generate
    :return: the response from the server
    """
    
    output_path = f'{path}/tmp/data/video_prompt.json'

    message = f'Generate a {settings["video"]["prompts"]} image prompts for the theme {topic}. Code only in the format of [[num, prompt], [num, prompt], ...] start at 0.'

    response = ""
    for chunk in client.send_message("chinchilla", message, with_chat_break=True):
        response += chunk["text_new"]
    # output the response to a new json file  with the name of the theme
    with open(output_path, "w") as f:
        template = Template("""
        {
        "prompts": {
            "data": $prompts,
            "headers": ["Start at second [0,1,...]", "Prompt"]
        },
        "negPrompt": "frames, border, edges, borderline, text, character, duplicate, error, out of frame, watermark, low quality, ugly, deformed, blur, bad-artist",
        "prePrompt": "",
        "postPrompt": "epic perspective,(vegetation overgrowth:1.3)(intricate, ornamentation:1.1),(baroque:1.1), fantasy, (realistic:1) digital painting , (magical,mystical:1.2) , (wide angle shot:1.4), (landscape composed:1.2)(medieval:1.1),(tropical forest:1.4),(river:1.3) volumetric lighting ,epic, style by Alex Horley Wenjun Lin greg rutkowski Ruan Jia (Wayne Barlowe:1.2)"
        }"""
        )
        f.write(template.substitute(prompts=response[response.find("[") : response.rfind("]") + 1]))
    return output_path

def generate_audio_prompts(topic,tmp_path):
    """
    Get a list of prompts for a given theme that makes musicly sense
    """
    voice_duration = FFProbe(f'{tmp_path}/dist/voice.mp3').audio[0].duration
    print(voice_duration)
    try:
        response = ""
        prompt = f"""generate a python list only with {round(float(voice_duration) - 3 / 20)} prompts for the theme {topic} that makes musicly sense, here is an example of what the format should look like also ignore the theme of the example and only do the given theme: ["A sea shanty in the key of G minor with a tempo of 90 bpm that tells the tale of a pirate ship's crew hoisting the Jolly Roger for the first time.", "A dramatic orchestral piece in the key of D minor with a tempo of 140 bpm that captures the intensity of a pirate ship battle at sea.", "A lively jig in the key of A major with a tempo of 120 bpm that celebrates a successful raid by a pirate ship on a wealthy merchant vessel."] I want code only and one line and make sure to use doublequotes for each item"""
        for chunk in client.send_message("a2", prompt, with_chat_break=True):
            response += chunk["text_new"]
        final_response = response[response.find("[") : response.rfind("]") + 1]
        return ast.literal_eval(final_response)
    except:
        return generate_audio_prompts(topic,tmp_path)

def get_video(path, prompt_path):

    output_path = f'{path}/dist/background.mp4'

    browser_options = webdriver.FirefoxOptions()

    if settings["browser"]["headless"]:
        browser_options.add_argument("--headless")

    driver = webdriver.Firefox(options=browser_options)
   

    driver.get("http://127.0.0.1:7860/")
    assert "Stable Diffusion" in driver.title
    # click the ubtton that says infinite zoom

    driver.find_element(By.XPATH, "//button[text()='Infinite Zoom']").click()
    # click the button that says Infinite Zoom
    # wait for page to load
    # scroll down to the bottom of the page
    # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    driver.find_element(By.XPATH, "//button[text()='Clear prompts']").click()

    # remove the hide class from the input 
    driver.find_element(By.XPATH, "//input[contains(@class, 'hide')]").send_keys(os.path.abspath(prompt_path))
    

    # find input box next to the label that says "Output Width" and set the value to 432 delete everything in the box and type 432 
    driver.find_element(By.XPATH, "//span[text()='Total video length [s]']/following-sibling::input[@type='number']").clear()
    driver.find_element(By.XPATH, "//span[text()='Total video length [s]']/following-sibling::input[@type='number']").send_keys(settings["video"]["duration"])

    driver.find_element(By.XPATH, "//label[@for='range_id_90']/following-sibling::input[@type='number']").clear()
    driver.find_element(By.XPATH, "//label[@for='range_id_90']/following-sibling::input[@type='number']").send_keys(settings["video"]["width"])

    driver.find_element(By.XPATH, "//label[@for='range_id_91']/following-sibling::input[@type='number']").clear()
    driver.find_element(By.XPATH, "//label[@for='range_id_91']/following-sibling::input[@type='number']").send_keys(settings["video"]["height"])

    driver.find_element(By.XPATH, "//label[@for='range_id_93']/following-sibling::input[@type='number']").clear()
    driver.find_element(By.XPATH, "//label[@for='range_id_93']/following-sibling::input[@type='number']").send_keys(settings["video"]["iterations"])

    driver.find_element(By.XPATH, "//button[text()='Video']").click()

    driver.find_element(By.XPATH, "//label[@for='range_id_95']/following-sibling::input[@type='number']").clear()
    driver.find_element(By.XPATH, "//label[@for='range_id_95']/following-sibling::input[@type='number']").send_keys(0)

    driver.find_element(By.XPATH, "//label[@for='range_id_96']/following-sibling::input[@type='number']").clear()
    driver.find_element(By.XPATH, "//label[@for='range_id_96']/following-sibling::input[@type='number']").send_keys(0)

    driver.find_element(By.XPATH, "//label[@for='range_id_97']/following-sibling::input[@type='number']").clear()
    driver.find_element(By.XPATH, "//label[@for='range_id_97']/following-sibling::input[@type='number']").send_keys(settings["video"]["slowness"])
    
    driver.find_element(By.XPATH, f"//input[@value='{settings['video']['mode']}']")
    


    driver.find_element(By.XPATH, "//button[text()='Post proccess']").click()

    driver.find_element(By.XPATH, "//label[@for='range_id_99']/following-sibling::input[@type='number']").clear()
    driver.find_element(By.XPATH, "//label[@for='range_id_99']/following-sibling::input[@type='number']").send_keys(settings["video"]["upscale"])
    # use javascript to click the checkbox that says "Enable Upscale"
    driver.find_element(By.XPATH, "//span[text()='Enable Upscale']/preceding-sibling::input").click()





    driver.find_element(By.XPATH, "//div[@id='infZ_upscaler']//input[@autocomplete='off']").click()
    # Keys.DOWN,Keys.DOWN,
    driver.find_element(By.XPATH, "//div[@id='infZ_upscaler']//input[@autocomplete='off']").send_keys(Keys.DOWN,Keys.ENTER)

    time.sleep(5)

    driver.find_element(By.XPATH, "//button[text()='Generate video']").click()

    # wait for a element to appear that says "Download video"

    WebDriverWait(driver, timeout=60*30).until(lambda d: d.find_element(By.XPATH, "//button[@aria-label='Download']"))

    # click the button with the aria label that says "Download"
    driver.find_element(By.XPATH, "//button[@aria-label='Download']").click()
    # move the latest file in the downloads folder to the output folder and rename it to main.mp4
    time.sleep(5)
    driver.quit()
    shutil.move(get_files("C:/Users/drew/Downloads")[0], output_path)

    return output_path

def get_files(dirpath):
    file_names = os.listdir(dirpath)
    file_names.sort(key=lambda s: os.path.getmtime(os.path.join(dirpath, s)), reverse=True)
    return [f"{dirpath}/{file_name}" for file_name in file_names]

def get_music(prompts, tmp_path):
    """
    Uses selenium to generate music
    """

    browser_options = webdriver.FirefoxOptions()
    browser_options.add_argument('-profile')
    browser_options.add_argument('C:/Users/drew/AppData/Roaming/Mozilla/Firefox/Profiles/dlionb1w.default-release')

    if settings["browser"]["headless"]:
        browser_options.add_argument("--headless")



    driver = webdriver.Firefox(options=browser_options)
    # open a new tab
    with open(f"{tmp_path}/tmp/data/music_prompts.json", "w") as f:
       template = Template("""{ "prompts": $prompts, }""")
       f.write(template.substitute(prompts=prompts))

   
  
    output_path = f'{tmp_path}/dist/music.mp3'
    tmp_music_path = f'{tmp_path}/tmp/music'
    print("Generating music")


    actions = ActionChains(driver)

    is_list = type(prompts) == list
    count = 0
    error_count = 0

    driver.get("https://aitestkitchen.withgoogle.com/experiments/music-lm")

    try:
        driver.find_element(By.XPATH, "//button[contains(text(),'Get started')]").click()
        driver.find_element(By.XPATH, "//button[contains(text(),'Sign in now')]").click()
        time.sleep(3)
        driver.get("https://aitestkitchen.withgoogle.com/experiments/music-lm")
        time.sleep(2)
    except:
        pass
    while True:
        try:
            WebDriverWait(driver, timeout=60).until(lambda d: d.find_element(By.XPATH, "//textarea"))
            print(count)
            if count >= len(prompts) or not is_list or error_count > 5:
                break
            driver.find_element(By.XPATH, "//textarea").clear()
            driver.find_element(By.XPATH, "//textarea").send_keys(prompts[count] if is_list else prompts, Keys.ENTER)
            time.sleep(7.5)
            random_choice = random.randint(0, 1)
            driver.find_elements(By.XPATH, "//button[@aria-label='More options']")[random_choice + 1].click()
            # use javascript to click the button the role is menuitem and the inner text is "Download"
            # driver.execute("document.querySelector('button[role=menuitem][inner-text=Download]').click()")
            actions.send_keys(Keys.DOWN,Keys.DOWN, Keys.DOWN,Keys.DOWN, Keys.ENTER).perform()
            time.sleep(3)
            shutil.move(get_files('C:/Users/drew/Downloads')[0], tmp_music_path)
            count += 1
            driver.get("https://aitestkitchen.withgoogle.com/experiments/music-lm")        
        except Exception as e:
            print(e)
            error_count += 1
            pass
    webdriver.Firefox.quit(driver)
    if error_count > 5:
        print("Too many errors, falling back to default music")
        shutil.copyfile("D:/Programming/Automation/Stable_Diffusion_Videos/assets/fallback/music.mp3", output_path)
        raise Exception("Too many errors")

    print("Combining music files")

    files = get_files(tmp_music_path)
    stream = [ffmpeg.input(file) for file in files]
    # for each file that is connected add a crossfade for the last 2 seconds
    for i in range(len(stream) - 1):
        stream[i] = ffmpeg.filter([stream[i], stream[i + 1]], 'acrossfade',d=3)

    stream = ffmpeg.concat(*stream, v=0, a=1)
    # make sure that the audio will never be too high and loud
    stream = ffmpeg.filter(stream, 'highpass', f=200)
    stream = ffmpeg.filter(stream, 'acompressor', threshold="-20dB", ratio=9, attack=200, release=1000)
    stream = ffmpeg.filter(stream, 'loudnorm', i=-16, tp=-1.5, lra=11, print_format='summary')
    stream = ffmpeg.filter(stream, 'volume', volume=0.5)
    stream = ffmpeg.output(stream, f'{tmp_music_path}/music_tmp.mp3')
    ffmpeg.run(stream)
    print("Done combining music files")

    metadata = FFProbe(f'{tmp_music_path}/music_tmp.mp3')
    duration = metadata.streams[0].duration

    stream_1 = ffmpeg.input(f'{tmp_music_path}/music_tmp.mp3')
    stream_1 = ffmpeg.filter(stream_1, 'afade', t="out", st=round(float(duration)) - 5, d=5)
    stream_1 = ffmpeg.filter(stream_1, 'afade', t="in", st=0, d=5)
    stream_1 = ffmpeg.output(stream_1, output_path)
    ffmpeg.run(stream_1)

    return output_path



    # # get all the files in the downloads folder and sort them by latest

    # move the latest file to the assets folder

def get_voice(topic, prompt, tmp_path):
    """
    Get's the voice from the locally running conqui ai docker container or service
    """
    tmp_output_path = f'{tmp_path}/tmp/audio/voice.wav'
    output_path = f'{tmp_path}/dist/voice.mp3'

    text = f"{settings['voice']['intro']} {topic}. {prompt} {settings['voice']['outro']}"
    res = requests.get(f"""http://localhost:5002/api/tts?text={text}&speaker_id={settings['voice']['speaker']}&style_wav=&language_id= HTTP/1.1""")
    with open(tmp_output_path, 'wb') as f:
        f.write(res.content)
    
    stream = ffmpeg.input(tmp_output_path)
    stream = ffmpeg.output(stream, output_path)
    ffmpeg.run(stream)

    return output_path

def get_transcript(tmp_path, voice_path):
    output_path = f'{tmp_path}/dist/subtitle.srt'
    model = whisper.load_model("large") # Change this to your desired model
    print("Whisper model loaded.")
    transcribe = model.transcribe(audio=voice_path, word_timestamps=True)
    # output the transcripbe to a temp file
    with open(f'{tmp_path}/tmp/data/transcript.json', 'w') as f:
        f.write(str(transcribe))
    segments = transcribe['segments']
    for segment in segments:
        words = segment['words']
        for i in range(len(words)):
            word = words[i]
            time = lambda x: f'0{datetime.timedelta(seconds=x)}'.replace('.', ',')
            start_time = time(word["start"]).removesuffix('000') if len(time(word["start"])) > 8 else f'0{time(word["start"])},000'
            end_time = time(word["end"]).removesuffix('000') if len(time(word["end"])) > 8 else f'0{time(word["end"])}'
            with open(output_path, "a") as f:
                f.write(f"{i+1}\n{start_time} --> {end_time}\n{word['word'].removeprefix(' ')}\n\n") 
    # replacethe 11th line with NeoClipse
    with open(output_path, 'r') as f:
        lines = f.readlines()
    lines[10] = "NeoClipse,\n"
    with open(output_path, 'w') as f:
        f.writelines(lines)
        
    return output_path

def voice_pipline(topic, tmp_path):
    story = generate_generic_prompt(f'Generate a story about {topic}', model='chinchilla') # Poe
    with open(f'{tmp_path}/tmp/data/story.txt', 'w') as f:
        f.write(story)
    get_voice(topic, story, tmp_path) # Coqui AI

def video_pipeline(topic,tmp_path): # Finished
    video_json_path = generate_video_prompts(topic, tmp_path) # Poe
    get_video(tmp_path, video_json_path) # SD

def music_pipeline(topic, tmp_path):
    music_prompt_res = generate_audio_prompts(topic, tmp_path) # Poe
    get_music(music_prompt_res, tmp_path) # Google LM

def transcription_pipline(tmp_path):
    get_transcript(tmp_path, f'{tmp_path}/dist/voice.mp3') # Whisper

def main():

    topic = generate_generic_prompt('Generate a one to three word topic for a viral video in the style of Reddit or Quora')
    background_topic = generate_generic_prompt(f'Generate a one to three word landscape or object that relates to the topic {topic}')
    print(f"Topic: {topic}")
    now = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    tmp_path = f"D:/Programming/Automation/Stable_Diffusion_Videos/assets/{now}"

    
    # delete what is in the public folder
    shutil.rmtree("D:/Programming/Automation/Stable_Diffusion_Videos/editor/public")
    shutil.copytree("D:/Programming/Automation/Stable_Diffusion_Videos/asset_folder_structures", tmp_path)
 
    thread_1 = Thread(target=video_pipeline, args=(background_topic,tmp_path,))
    thread_2 = Thread(target=voice_pipline, args=(topic,tmp_path,))
    thread_3 = Thread(target=music_pipeline, args=(topic,tmp_path,))
    thread_4 = Thread(target=transcription_pipline, args=(tmp_path,))
    # we need the voice pipleine done before we can start hthe music and the transcription pipeline
    thread_1.start()
    thread_2.start()
    thread_2.join()
    thread_3.start()
    thread_4.start()
    thread_1.join()
    thread_3.join()
    thread_4.join()

    

    # copy all the files from the tmp folder to the public folder
    for file in os.listdir(f"{tmp_path}/dist"):
        shutil.copyfile(f"{tmp_path}/dist/{file}", f"D:/Programming/Automation/Stable_Diffusion_Videos/editor/public/{file}")
    os.chdir("D:/Programming/Automation/Stable_Diffusion_Videos/editor")
    os.system("yarn build")

    shutil.move("D:/Programming/Automation/Stable_Diffusion_Videos/editor/out/final.mp4", f"D:/Programming/Automation/Stable_Diffusion_Videos/out/{now}-{topic}.mp4")

if __name__ == "__main__":
    # see how much time it takes to run the script human readable
    while True:
        start = time.time()
        main()
        end = time.time()
        print(f"Time taken: {datetime.timedelta(seconds=end-start)}")
        time.sleep(60*5)


