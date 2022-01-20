import os
import tkinter as tk
import matplotlib.pyplot as plt
import pandas as pd

# Need "--hidden-import pandas.plotting._matplotlib" when running auto-py-to-exe

class Perecentage(tk.Tk):

    record = pd.DataFrame(columns=['sessions','percentage'])

    def __init__(self, directory):

        if os.path.isdir(directory):
            for entry in os.scandir(directory):
                if entry.path.endswith('.csv') and entry.is_file():

                    cvs_df = pd.read_csv(entry.path)

                    cvs_df.astype({'pass': 'float'}).dtypes
                    cvs_df.astype({'fail': 'float'}).dtypes

                    total_fails = cvs_df['fail'].sum()
                    total_passes = cvs_df['pass'].sum()
                    total_attempts = total_fails + total_passes
                    percent_correct = (total_passes / total_attempts) * 100

                    if(total_attempts > 60):

                       #print(entry.name + ' : ' +str(total_fails) + ' + ' + str(total_passes)  + ' = ' + str(total_attempts) + ' : ' + str(percent_correct) + '%')

                        if self.record.empty:
                            self.record = pd.DataFrame([[entry.name, (cvs_df['pass'].sum() / (cvs_df['pass'].sum() + cvs_df['fail'].sum())) * 100]], columns=['sessions', 'percentage'])
                        else:
                            self.record.loc[len(self.record.index)] = [entry.name, (cvs_df['pass'].sum() / (cvs_df['pass'].sum() + cvs_df['fail'].sum())) * 100]

        print('Last run average:' + str(percent_correct))
        print('Running average:' + str(self.record['percentage'].mean()))

    def plot(self):

        df = self.record
        df.set_index('sessions', inplace=True)

        df.plot.line(rot=0, color={'percentage':'blue'}, title='ICR Percentage')

        plt.gca().axes.get_xaxis().set_visible(False)

        plt.show()


def main(directory):

  status = Perecentage(directory)
  status.plot()

if __name__ == '__main__':
  import sys, argparse

  parser = argparse.ArgumentParser(description='Convert text to morse code audio.')
  parser.add_argument('--dir', type=str, default='scores', help='Number of phrases to generate')
  args = parser.parse_args()

  main(args.dir)