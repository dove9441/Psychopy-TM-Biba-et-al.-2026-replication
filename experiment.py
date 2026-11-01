from psychopy import core, event, monitors, visual
from pathlib import Path
import random
import pandas as pd
from datetime import datetime


script_dir = Path(__file__).parent
stim_dir = script_dir /  "stim"
results_dir = script_dir / "results"
results_dir.mkdir(exist_ok=True)


BACKGROUND_COLOR = [244, 241, 241]
BLUE = [50, 116, 181]
ORANGE = [226, 121, 46]
# BLOCK = 1
KEY_MAP = {"h": "new", "j": "old", "k": "I/O", "l": "SZ"}


# *모니터 주사율 60Hz 확인하기*
#monitor = monitors.Monitor("labMonitor", width=30.2, distance=50.0) # # MacBook pro 14" -> 30.2cm width
monitor = monitors.Monitor("labMonitor", width=59.7, distance=74.0) # desktop

#monitor.setSizePix((1800, 1169)) # macbook pro 14"
#monitor.setSizePix((1280, 832)) #  macbook air 13"
monitor.setSizePix((1920, 1080)) # desktop




def quit_exp():
    win.close()
    core.quit()



def make_SOA_sequence(): # 200ms ~ 1100ms (33.33ms step) 
    SOA_frame_list = list(range(12, 67, 2)) 
    SOA_ms_list = [frames * (1000 / 60) for frames in SOA_frame_list] # [200.0, 233.33333333333334, 266.6666666666667, 300.0, 333.33333333333337, ..., 1100.0]
    SOA_frame_list *= 2
    random.shuffle(SOA_frame_list) # [44, 56, 24, 32, 18, 48, 14, 12, 40, 30, 64, 16, 52, 38, 20, 36, 34, 60, 62, 54, 46, 66, 26, 42, 22, 28, 58, 50]
    return SOA_frame_list, SOA_ms_list


def make_cue_sequence(n_each=28, max_run=3):
    cues = ["blue"] * n_each + ["orange"] * n_each
    while True:
        random.shuffle(cues)

        if all(len(set(cues[i : i + max_run + 1])) > 1 for i in range(len(cues) - max_run)):
            return cues
        
def make_stimulus_sequence(BLOCK):
    img_split_df = pd.read_csv(f'{script_dir}/test_split.csv')
    img_block_df = img_split_df.loc[img_split_df['block'] == BLOCK]
    img_block_old = img_block_df.loc[img_block_df['label'] == 'old']
    img_block_new = img_block_df.loc[img_block_df['label'] == 'new']

    img_list_old = list(img_block_old.iloc[:,0])
    img_list_new = list(img_block_new.iloc[:,0])

    random.shuffle(img_list_old)
    random.shuffle(img_list_new)

    # old 56장 + new 28장 합쳐서 랜덤 순서로 섞기
    img_combined = (
        [(img, 'old') for img in img_list_old] +
        [(img, 'new') for img in img_list_new]
    )
    random.shuffle(img_combined) # [(file_name, label), ...]

    return img_list_old, img_list_new, img_combined







win = visual.Window( 
    #size=(1800, 1169),
    fullscr=True,
    monitor=monitor,
    units="deg",
    color=BACKGROUND_COLOR,
    colorSpace="rgb255"
)



fixation_cross = visual.TextStim(
    win,
    text="+",
    color="black",
    height=1.8,
    pos=(0,0)
)

question = visual.TextStim(
    win,
    text="indoor outdoor?",
    color=BLUE,
    colorSpace="rgb255",
    height=1.5,
)

#######################################################
## Experiment starts

for BLOCK in range(1,9): # 1~8 연속으로, 끊어서 할 시 조정

    instruction = visual.TextStim(
        win,
        text="indoor : 'i' / outdoor : 'o'\nbig : 'i' / small : 'o'\n\npress 'space' to continue. ",
        color="black",
        height=1.3,
    )
    ## Instruction
    instruction.draw()
    win.flip()
    keys = event.waitKeys(keyList=["space", "escape"])
    if keys and keys[0] == "escape":
        quit_exp()

    cue_sequence = make_cue_sequence(n_each=28, max_run=3) # [ 'blue', 'blue', 'orange' , ...]
    SOA_frame_sequence, SOA_ms_sequence = make_SOA_sequence()  # shuffled SOA : ex) [52, 16, 22, 40, 62, 30, 60, 20, 34, 44, ...]
    img_list_old, img_list_new, _  = make_stimulus_sequence(BLOCK)


    stim = []
    block = []
    trial_num = []
    response = []
    RT = []
    task_type = []
    expected_SOA = []
    actual_SOA = []
    stim_type_dict = {}


    ## Encoding trial loop
    for trial in range(56):
        # Stimulus setup (to prevent stimulation delay)
        image = visual.ImageStim(
        win,
        image=str(stim_dir / img_list_old[trial]),
        pos=(0, 0),
        size=(13, 13))

        if cue_sequence[trial] == "blue":
            question.text = "Indoor outdoor?"
            question.color = BLUE
        else:
            question.text = "Big small?"
            question.color = ORANGE
        ###
        
        # Fixation 1 (cross)
        fixation_duration = random.randint(13, 17) # 1300ms ~ 1700ms intertrial interval

        for frames in range(fixation_duration*6): # 1300ms ~ 1700ms -> 78 ~ 102 frames
            fixation_cross.draw()
            win.flip()


        # Cue(color background)
        if cue_sequence[trial] == "blue":
            win.color = BLUE
        else:
            win.color = ORANGE

        for frames in range(6): # 100ms
            fixation_cross.draw()
            win.flip()

        # Fixation 2 (Recover to original background)
        win.color = BACKGROUND_COLOR
        SOA_clock = core.Clock()
        for frames in range(SOA_frame_sequence[trial]):
            fixation_cross.draw()
            if frames == 0:
                win.callOnFlip(SOA_clock.reset)
            win.flip()


        # Stimulus
        response_clock = core.Clock()
        response_key = None
        response_rt = None
        actual_SOA_ms = {"time": None}

        event.clearEvents(eventType="keyboard")
        for frames in range(30): # 500ms
            image.draw()
            if frames == 0:
                win.callOnFlip(response_clock.reset)
                win.callOnFlip(lambda: actual_SOA_ms.update({"time": SOA_clock.getTime() * 1000}))
            win.flip()

            if response_key is None:
                keys = event.getKeys(
                    keyList=["i", "o", "escape"], # Indoor/Big : i, Outdoor/Small : o
                    timeStamped=response_clock,
                )
                if keys:
                    response_key, response_rt = keys[0] # [['k', 0.5950590833381284]] 
                    if response_key == "escape":
                        quit_exp()

        for frames in range(150): # 2500ms -> 2.5*60=150 frames
            question.draw()
            win.flip()

            if response_key is None:
                keys = event.getKeys(
                    keyList=["i", "o", "escape"],
                    timeStamped=response_clock,
                )
                if keys:
                    response_key, response_rt = keys[0]
                    if response_key == "escape":
                        quit_exp()
        

        # Store statistics    
        stim.append(str(img_list_old[trial]))
        block.append(BLOCK)
        trial_num.append(trial+1)
        expected_SOA.append(SOA_frame_sequence[trial] * (1000 / 60))
        actual_SOA.append(actual_SOA_ms["time"])

        if response_rt is None:
            RT.append(None)
        else:
            RT.append(response_rt)

        if cue_sequence[trial] == "blue":
            task_type.append('I/O')
            stim_type_dict[str(img_list_old[trial])] = 'I/O'

            if response_rt is None:
                response.append(None)
            else:
                if response_key == 'i':
                    response.append('indoor')
                else:
                    response.append('outdoor')
        else:
            task_type.append('SZ')
            stim_type_dict[str(img_list_old[trial])] = 'SZ'

            if response_rt is None:
                response.append(None)
            else:
                if response_key == 'i':
                    response.append('big')
                else:
                    response.append('small')


    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = results_dir / f"encoding_block_{BLOCK}_{timestamp}.csv"

    pd.DataFrame({
                    "stim" : stim,
                    "block" : block,
                    'trial_num' : trial_num,
                    "RT": RT,
                    "task_type" : task_type,
                    "response": response,
                    "expected_SOA" : expected_SOA,
                    "actual_SOA" : actual_SOA
                }).to_csv(output_path, index=False)



    ###################################
    ### Retrieval



    # print("Actual Frame Rate:", win.getActualFrameRate()) #test

    instruction = visual.TextStim(
        win,
        text="new : press 'H'\nold : press 'J'\nIndoor/Outdoor : press 'K' \nSize : press 'L'\n\npress 'space' to continue.",
        color="black",
        height=1.3,
    )


    response_label = visual.TextBox2(
        win,
        text=(
            "H = New     "
            "J = Old     "
            "K = <c=#3274B5>I/O</c>     "
            "L = <c=#E2792E>SZ</c>     "
        ),
        color="black",
        letterHeight=1.0,
        pos=(0, -12),
        alignment="center",
        borderWidth=0,
        fillColor=None,
    )


    ## Experiment starts

    ## Instruction
    instruction.draw()
    win.flip()                    
    keys = event.waitKeys(keyList=["space", "escape"])
    if keys and keys[0] == "escape":
        quit_exp()

    _, _, img_list = make_stimulus_sequence(BLOCK)

    stim = []
    block = []
    trial_num = []
    response = []
    RT = []
    trial_duration = [] #test

    label= []
    correct = []

    #반응시간(RT)를 측정할 시계
    response_clock = core.Clock()
    trial_clock = core.Clock() #test

    ## Trial loop
    for trial, (img_name, img_label) in enumerate(img_list):

        # Stimulus setup (to prevent stimulation delay)
        image = visual.ImageStim(
            win,
            image=str(stim_dir / img_name),
            pos=(0, 0),
            size=(13, 13),
        )

        response_key = None
        response_rt = None
        event.clearEvents(eventType="keyboard")
        trial_clock.reset() #test

        for frames in range(180):  # 3000ms -> 3*60=180 frames
            image.draw()
            response_label.draw()
            if frames == 0:
                win.callOnFlip(response_clock.reset)
            win.flip()

            if response_key is None:
                keys = event.getKeys(
                    keyList=["h", "j", "k", "l", "escape"],
                    timeStamped=response_clock,
                )
                if keys:
                    response_key, response_rt = keys[0]
                    if response_key == "escape":
                        quit_exp()
                    break

        # Store statistics
        stim.append(img_name)
        block.append(BLOCK)
        trial_num.append(trial + 1)
        RT.append(response_rt)
        response.append(KEY_MAP.get(response_key) if response_key else None)
        label.append(img_label)
        
        if img_label =='old':
            correct.append(1 if stim_type_dict[img_name] == KEY_MAP.get(response_key) else 0)
        else:
            correct.append(None)

        trial_duration.append(trial_clock.getTime()) #test
        #print(f"Trial {trial+1}: {trial_clock.getTime():.4f} sec")


    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = results_dir / f"retrieval_block_{BLOCK}_{timestamp}.csv"

    pd.DataFrame({
        "stim": stim,
        "block": block,
        "trial_num": trial_num,
        "RT": RT,
        "response": response,
        "label" : label,
        'correct' : correct,
        "trial_duration": trial_duration, #test
    }).to_csv(output_path, index=False)

## BLOCK Loop
#######################

visual.TextStim(
        win,
        text="End.",
        color="black",
        height=1.3,
    ).draw()
win.flip()
core.wait(3)

win.close()
core.quit()
