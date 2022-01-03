import gui

def main(filename):

  status = gui.status(filename)
  status.plot()

if __name__ == '__main__':
  import sys, argparse

  parser = argparse.ArgumentParser(description='Convert text to morse code audio.')
  parser.add_argument('--file', type=str, default='record.csv', help='Number of phrases to generate')
  args = parser.parse_args()

  main(args.file)

