import subprocess

bashCommand = "happifyml azure --register test_gpt_gpu_1644331916_408766a6 --model-name=test --model-path=logs/runs/2022-02-08/14-53-31-pos_neg_neutral/"
process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
output, error = process.communicate()
