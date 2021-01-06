"""
This the the main program of the project
"""
import fire_analysis

if __name__ == '__main__':
    while True:
        print('-' * 40,
              '\nWelcome to our project, we can provide you with',
              '\n1. The relationship between the year and average maximum temperature',
              '\n2. The relationship between the year and average minimum temperature',
              '\n3. The relationship between maximum temperature of a day and fire intensity',
              '\n4. The relationship between minimum temperature of a day and fire intensity',
              '\n5. The prediction of wildfire intensity in a year',
              '\n6. The visual map of wildfire in a certain month')
        option = input('\033[33mEnter the number of the option to see more...\033[0m\n')
        if option not in ['1', '2', '3', '4', '5', '6']:
            print('\033[31mInvalid option\033[0m')
        else:
            if option == '1':
                fire_analysis.plot_year_to_temp('max')
            elif option == '2':
                fire_analysis.plot_year_to_temp('min')
            elif option == '3':
                fire_analysis.plot_temp_vs_fire_intensity('max')
            elif option == '4':
                fire_analysis.plot_temp_vs_fire_intensity('min')
            elif option == '5':
                year = input('\033[33mPlease enter a year for the prediction...\033[0m\n')
                if year.isdigit():
                    print('\033[34m' + fire_analysis.make_prediction(int(year)) + '\033[0m')
                else:
                    print('\033[31mInvalid year\033[0m')
            elif option == '6':
                year = input('\033[33mPlease enter a year (2007 - 2015)'
                             ' as a integer for the wildfire map...\033[0m\n')
                month = input('\033[33mPlease enter a month (January - December)'
                              ' as a string for the wildfire map...\033[0m\n')
                if year.isdigit() and 2007 <= int(year) <= 2015 and month in fire_analysis.MONTH:
                    fire_analysis.plot(month, int(year))
                else:
                    print('\033[31mInvalid year or month\033[0m')
        print('\n')
