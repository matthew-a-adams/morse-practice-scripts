import gui

# Need "--hidden-import pandas.plotting._matplotlib" when running auto-py-to-exe

def main(directory):

  status = gui.status(directory)
  status.plot()

if __name__ == '__main__':
  import sys, argparse

  parser = argparse.ArgumentParser(description='Convert text to morse code audio.')
  parser.add_argument('--dir', type=str, default='scores', help='Number of phrases to generate')
  args = parser.parse_args()

  main(args.dir)

