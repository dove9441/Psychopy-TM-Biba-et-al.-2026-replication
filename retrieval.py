from psychopy import core, event, monitors, visual
from pathlib import Path
import random
import pandas as pd
from datetime import datetime


script_dir = Path(__file__).parent
stim_dir = script_dir / "stim"

#결과를 저장할 폴더 생성
results_dir = script_dir / "results"
results_dir.mkdir(exist_ok=True)


BACKGROUND_COLOR = [244, 241, 241]
BLOCK = 1


def quit_exp():
    win.close()
    core.quit()


def make_stimulus_sequence(BLOCK):
    img_split_df = pd.read_csv(f'{script_dir}/test_split.csv')
    img_block_df = img_split_df.loc[img_split_df['block'] == BLOCK]
    img_block_old = img_block_df.loc[img_block_df['label'] == 'old']
    img_block_new = img_block_df.loc[img_block_df['label'] == 'new']

    img_list_old = list(img_block_old.iloc[:, 0])
    img_list_new = list(img_block_new.iloc[:, 0])

    # old 56장 + new 28장 합쳐서 랜덤 순서로 섞기
    img_combined = (
        [(img, 'old') for img in img_list_old] +
        [(img, 'new') for img in img_list_new]
    )
    random.shuffle(img_combined)
    return img_combined  # [(file_name, label), ...]


# MacBook Air 13"
monitor = monitors.Monitor("labMonitor", width=30.2, distance=100.0)
#monitor.setSizePix((1800, 1169)) #MacBook Pro 14
monitor.setSizePix((1280, 832))

win = visual.Window(
    fullscr=True,
    monitor=monitor,
    units="deg",
    color=BACKGROUND_COLOR,
    colorSpace="rgb255",
)

print("Actual Frame Rate:", win.getActualFrameRate()) #test

# key랑 응답 매칭
KEY_MAP = {"h": "new", "j": "old", "k": "I/O", "l": "SZ"}

instruction = visual.TextStim(
    win,
    text="new : press 'H'\nold : press 'J'\nIndoor/Outdoor : press 'K' \nSize : press 'L'\n\npress 'space' to continue.",
    color="black",
    height=0.5,
)

response_label = visual.TextStim(
    win,
    text="H = New          J = Old          K = I/O          L = SZ",
    color="black",
    height=0.45,
    pos=(0, -5),
)

response_label = visual.TextBox2(
    win,
    text=(
        "H = New          "
        "J = Old          "
        "K = <c=#3274B5>I/O</c>          "
        "L = <c=#E2792E>SZ</c>"
    ),
    color="black",
    letterHeight=0.45,
    pos=(0, -5),
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

img_list = make_stimulus_sequence(BLOCK)

stim = []
block = []
trial_num = []
response = []
RT = []
trial_duration = [] #test

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
        size=(5, 5),
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

    # Store statistics
    stim.append(img_name)
    block.append(BLOCK)
    trial_num.append(trial + 1)
    RT.append(response_rt)
    response.append(KEY_MAP.get(response_key) if response_key else None)

    trial_duration.append(trial_clock.getTime()) #test
    print(f"Trial {trial+1}: {trial_clock.getTime():.4f} sec")

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_path = results_dir / f"retrieval_block_{BLOCK}_{timestamp}.csv"

pd.DataFrame({
    "stim": stim,
    "block": block,
    "trial_num": trial_num,
    "RT": RT,
    "response": response,
    "trial_duration": trial_duration, #test
}).to_csv(output_path, index=False)

win.close()
core.quit()
