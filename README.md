Open Data Project:
Collaborated with Lidia Ataupillco Ramos, Payas Singh and Emery Smith.

User guide:
After launching the program, the user is prompted to enter the name of a database they want to work with. If the name entered is not an existing database, a new database file will be created. After the database is selected, a textual interface (the main menu) appears that lists the available functions and gives the option to quit the program. 

An example of the input database is shown in the file sample.db

Some of these functions generate html files as output. When this happens, the html filename appears in the format “QX.html” if it is the first time the function was run and “QX-n.html” otherwise where X is the question number and n is the number denoting the first available filename in the above format.

A command line interface to analyze open data extracted from https://data.edmonton.ca. It provides 4 functionalities:

1. show_barplot_range
The user is prompted to enter a valid range year and a valid crime type. Next, the program generates a barplot of the number of incidents of the chosen crime type that occured in each month of the given range of years. Bar plot appears on screen as well as being saved as a png, and once the bar plot window is closed the program will return to the main menu.

2. most_least_populous
On selection of this function, the user is prompted for an integer n and then the function finds as many most/least populous areas to show on the map. Once the number is entered, a map is generated which is saved to a html file and the program will return to the main menu.

3. top_n_with_crime
When this function is selected, it first prompts for a range of years, with inclusive bounds. Then the program asks for a crime type to be selected. Next, the program asks for the number of areas to show on the map, after which the program will generate a map which is saved to a html file. Finally, the program returns to the main menu.

4. n_highest_crime_population_ratios
After selection of this function, the user will be prompted to enter a range of years [year1, year2] inclusive of the boundary years. Afterwards, the user is prompted to input the number of areas they want to see information for on the map. The function will generate as many areas with the highest crime to population ratios as well as the most common crime/s within the same area and range of years. After the number of areas to show is input, the output will be generated and can be found as an html file. After generating the output file, the main menu is returned to.
