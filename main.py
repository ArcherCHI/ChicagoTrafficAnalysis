#
# header comment! Overview, name, etc.
#
import datetime
import sqlite3
from matplotlib import text
import matplotlib.pyplot as plt



##################################################################  
#
# print_stats
#
# Given a connection to the database, executes various
# SQL queries to retrieve and output basic stats.
#

def single_row_query( dbConn, query ):
    dbCursor = dbConn.cursor()
    dbCursor.execute(query)
    row = dbCursor.fetchone() 
    if row == None: return 0
    else:
        return row[0] # Results come in a tuple with 1 element and a null 2nd element, so we reference the first.

def many_rows_query( dbConn, query ):
    dbCursor = dbConn.cursor()
    dbCursor.execute(query)
    rows = dbCursor.fetchall()
    return rows

def checkCameraID( dbConn, cameraID ):
    sql = "SELECT Camera_ID FROM RedCameras WHERE Camera_ID = '" + cameraID + "' UNION "
    sql += "SELECT Camera_ID FROM SpeedCameras WHERE Camera_ID = '" + cameraID + "';"
    res = single_row_query( dbConn, sql )
    if res == 0: return 0
    else: return 1

def print_menu():
    print("Select a menu option: ")
    print("  1. Find an intersection by name")
    print("  2. Find all cameras at an intersection")
    print("  3. Percentage of violations for a specific date")
    print("  4. Number of cameras at each intersection")
    print("  5. Number of violations at each intersection, given a year")
    print("  6. Number of violations by year, given a camera ID")
    print("  7. Number of violations by month, given a camera ID and year")
    print("  8. Compare the number of red light and speed violations, given a year")
    print("  9. Find cameras located on a street")
    print("or x to exit the program.")

def print_stats( dbConn ):
    print("General Statistics:")
    
    numRedLightCameras = single_row_query( dbConn, "SELECT COUNT(*) FROM RedCameras;" )
    print("  Number of Red Light Cameras:", f"{ numRedLightCameras:,}")
    
    numSpeedCameras = single_row_query( dbConn, "SELECT COUNT(*) FROM SpeedCameras;")
    print("  Number of Speed Cameras:", f"{ numSpeedCameras:,}")
    
    numRedEntries = single_row_query( dbConn, "SELECT COUNT( Num_Violations ) FROM RedViolations;" )
    print("  Number of Red Light Camera Violation Entries:", f"{numRedEntries:,}" )
    
    numSpeedEntries = single_row_query( dbConn, "SELECT COUNT( Num_Violations ) FROM SpeedViolations;" )
    print("  Number of Speed Camera Violation Entries:", f"{numSpeedEntries:,}" )

    earliestDate = single_row_query( dbConn, "SELECT Date( Violation_Date ) as Date FROM RedViolations GROUP BY Date ORDER BY Date LIMIT 1;" )
    latestDate = single_row_query( dbConn, "SELECT Date( Violation_Date ) as Date FROM RedViolations GROUP BY Date ORDER BY Date DESC LIMIT 1;" )
    print("  Range of Dates in the Database:", earliestDate, "-", latestDate )

    totalRedViolations = single_row_query( dbConn, "SELECT SUM( Num_Violations ) FROM RedViolations;" )
    print("  Total Number of Red Light Camera Violations:", f"{totalRedViolations:,}" )

    totalSpeedViolations = single_row_query( dbConn, "SELECT SUM( Num_Violations ) FROM SpeedViolations;" )
    print("  Total Number of Speed Camera Violations:", f"{totalSpeedViolations:,}" )

def option1( dbConn, sql ):
    rows = many_rows_query( dbConn, sql )
    if len( rows ) == 0:
        print("No intersections matching that name were found.")
        print()
        return
    for row in rows:
        print( row[0], ":", row[1] )
    print()

def option2( dbConn, redSQL, speedSQL ):
# Collect Red Camera Data
    redData = many_rows_query( dbConn, redSQL )
    print()
    # Query Checking
    if len( redData ) == 0:     # Check if data set is empty
        print("No red light cameras found at that intersection.")
        print()
    else :                           # Display if it's not.
        print("Red Light Cameras:")
        for row in redData:
            print( "  ", row[0], ":", row[1] )
        print() 

# Collecting Speed Camera Data
    speedData = many_rows_query( dbConn, speedSQL )
    if len( speedData ) == 0:                    # Check if data set is empty
        print("No speed cameras found at that intersection.")
        print()
    else:                                   # Otherwise, display the data
        print("Speed Cameras:")
        for row in speedData:
            print( "  ", row[0], ":", row[1] )
        print()

def option3( dbConn, redSQL, speedSQL ):
    numRedViolations = single_row_query( dbConn, redSQL )
# Check to see if results are empty, if red query is empty, then the speed query will be empty too.
    if numRedViolations == None:
        print("No violations on record for that date.")
        print()
        return
    numSpeedViolations = single_row_query( dbConn, speedSQL )

    totalViolations = numRedViolations + numSpeedViolations 
    redPercent = ( numRedViolations / totalViolations ) * 100
    speedPercent = ( numSpeedViolations / totalViolations ) * 100

    print("Number of Red Light Violations:", f"{ numRedViolations:,}", "({:.3f}%)".format( redPercent ) )
    print("Number of Speed Violations:", f"{ numSpeedViolations:,}", "({:.3f}%)".format( speedPercent ) ) 
    print("Total Number of Violations:", f"{ totalViolations:,}" )
    print()

def option4( dbConn, redSQL, speedSQL ):
# Counting Red Light Cameras Per Intersection
    redResults = many_rows_query( dbConn, redSQL )
    totalRedCameras = single_row_query( dbConn, "SELECT COUNT( DISTINCT Camera_ID ) FROM RedCameras;" )

# Counting Speed Cameras Per Intersection
    speedResults = many_rows_query( dbConn, speedSQL )
    totalSpeedCameras = single_row_query( dbConn, "SELECT COUNT( DISTINCT Camera_ID ) FROM SpeedCameras;" )

# Displaying Red Light Camera Info
    print("Number of Red Light Cameras at Each Intersection")
    for row in redResults:
        percentage = ( row[2] / totalRedCameras ) * 100
        print(" ", row[1], f"({row[0]})", ":", row[2], "({:.3f}%)".format( percentage ) ) 
    print()

# Displaying Speed Camera Info
    print("Number of Speed Cameras at Each Intersection")
    for row in speedResults:
        percentage = ( row[2] / totalSpeedCameras ) * 100
        print(" ", row[1], f"({row[0]})", ":", row[2], "({:.3f}%)".format( percentage ) ) 
    print()

def option5( dbConn, year, redSQL, speedSQL ):
# Collecting Data for Red Violations for Each Intersection given a year
    redResults = many_rows_query( dbConn, redSQL )

    # Query Checking
    print("Number of Red Light Violations at Each Intersection for " + year )
    if len( redResults ) == 0:
        print("No red light violations on record for that year.")
        print()
        print("Number of Speed Violations at Each Intersection for " + year )
        print("No speed violations on record for that year.")
        print()
        return
    
    # Query to collect total number of red light violations in given year
    totalRedSQL = "SELECT SUM( Num_Violations ) FROM RedViolations WHERE strftime('%Y', Violation_Date ) = '" + year + "';"
    totalRedViolations = single_row_query( dbConn, totalRedSQL )
    
    # Displaying Red Light Violation Data
    for row in redResults:
        percentage = ( row[2] / totalRedViolations ) * 100
        print(" ", row[0], f"({row[1]})", ":", f"{row[2]:,}", "({:.3f}%)".format( percentage ) )
    print("Total Red Light Violations in", year, ":", f"{totalRedViolations:,}" )
    print()

# Collecting Data for Speed Violations for Each Intersection given a year
    
    speedResults = many_rows_query( dbConn, speedSQL )

    # Query to collect total number of speed violations in given year
    totalSpeedSQL = "SELECT SUM( Num_Violations ) FROM SpeedViolations WHERE strftime('%Y', Violation_Date ) = '" + year + "';"
    totalSpeedViolations = single_row_query( dbConn, totalSpeedSQL )

    # Displaying Results
    print("Number of Speed Violations at Each Intersection for " + year )
    # Displaying Speed Violation Data
    for row in speedResults:
        percentage = ( row[2] / totalSpeedViolations ) * 100
        print(" ", row[0], f"({row[1]})", ":", f"{row[2]:,}", "({:.3f}%)".format( percentage ) )
    print("Total Speed Violations in", year, ":", f"{totalSpeedViolations:,}")

def option6( dbConn, cameraID, redSQL, speedSQL ):
# Collecting Data for Red Violations
    results = many_rows_query( dbConn, redSQL )
# Query Checking
    if len(results) == 0:   # No Data from Red Cameras 
        results = many_rows_query( dbConn, speedSQL )
    
# Arrays for Plot Coordinates
    years = []
    numViolations = []

# Displaying Results and Collecting Plot Coords
    print("Yearly Violations for Camera", cameraID )
    for row in results:
        print( row[0], ":", f"{row[1]:,}" )     # Each tuple is a (x,y) point
        years.append( row[0] )                      # Collects x-coords for plot
        numViolations.append( row[1] )              # Collects y-coords for plot
    print()
    
# Plot Setup & Display
    plotResponse = input("Plot? (y/n) ")
    print()
    if ( plotResponse == 'y' ):
        plt.plot( years, numViolations )
        plt.xlabel("Year")
        plt.ylabel("Number of Violations")
        plt.title("Yearly Violations for Camera " + cameraID )
        plt.show()
    else:
        plotResponse = 'x'

def option7( dbConn, year, cameraID, redSQL, speedSQL ):
# Collecting Data on Camera ID
    results = many_rows_query( dbConn, redSQL )

# Arrays for Plot Coordinates 
    months = []         # x coords
    numViolations = []  # y coords

# Displaying Data
    print("Monthly Violations for Camera", cameraID, "in", year )
    if len(results) == 0:                                # If cameraID not found in the red cameras,
        results = many_rows_query( dbConn, speedSQL )    # check the speed cameras
        if len(results) == 0:                            # At this point, all cameras in the database are checked
            print()                                      # It must be a problem with the year.
            plotResponse = input("Plot? (y/n) ")
            print()
            return
    for row in results:
        print( row[0] + "/" + year + " :", f"{row[1]:,}")
        months.append( row[0] )
        numViolations.append( row[1] )
    print()

    # Plot Setup
    plotResponse = input("Plot? (y/n) ")
    print()
    if plotResponse == 'y':
        plt.plot( months, numViolations )
        plt.xlabel("Month")
        plt.ylabel("Number of Violations")
        plt.title("Montly Violations for Camera " + cameraID + " (" + year + ")" )
        plt.show()
    else: plotResponse = 'x'

def option8( dbConn, year, redSQL, speedSQL ):
    redData = many_rows_query( dbConn, redSQL )
    speedData = many_rows_query( dbConn, speedSQL )

    # Check if query is empty
    if len( redData ) == 0:
        print("Red Light Violations:" )
        print("Speed Violations:" )
        print()
        input("Plot? (y/n)")
        print()
        return

    # Display data
    print("Red Light Violations:" )
    for i in range(5):                                  # Print first 5 elements
        print( redData[i][0], redData[i][1] )
    for i in range( len(redData) - 5, len(redData) ):   # Print last 5 elements
        print( redData[i][0], redData[i][1] )

    # Display Results
    print("Speed Violations:" )
    for i in range(5):                                  # Print first 5 elements
        print( speedData[i][0], speedData[i][1] )
    for i in range( len(speedData) - 5, len(speedData) ):   # Print last 5 elements
        print( speedData[i][0], speedData[i][1] )

# Plot Setup
    plotResponse = input("Plot? (y/n) ")
    print()
    if plotResponse == 'y': 
    # Arrays for Plot Coordinates
        days = []                   # x coords
        if ( int(year) % 4 == 0 ):
            numRedLightViolations = [0] * 366  # y coords
            numSpeedViolations = [0] * 366     # y coords 
            for i in range(1, 367):
                days.append(i)
        else:
            numRedLightViolations = [0] * 365  # y coords
            numSpeedViolations = [0] * 365     # y coords
            for i in range(1, 366):
                days.append(i)
    
        for i in range( len( redData ) ): 
            date = redData[i][0]              # points date to a tuple i.e. ( "2014-07-01", "4956" )

            y = int( date[ 0:4  ] )     # The datetime module does not convert strings to integers
            m = int( date[ 5:7  ] )     # We must convert each date to a counted day of the year 
            d = int( date[ 8:10 ] )     # i.e January 1st is Day 001

            idx = int(datetime.datetime( y, m, d ).strftime( "%j" )) - 1    # Converts date to a counted day, returns an idx to correspond
            numRedLightViolations[ idx ] = redData[i][1]                    # with our y-coord arrays
            numSpeedViolations[ idx ] = speedData[i][1]

        plt.plot( days, numRedLightViolations, color = 'red', label = "Red Light" )
        plt.plot( days, numSpeedViolations, color = 'orange', label = "Speed" )
        plt.xlabel("Day")
        plt.ylabel("Number of Violations")
        plt.title("Violations Each Day of " + year )
        plt.legend()
        plt.show()
    else: plotResponse = 'x'

def option9( dbConn, redSQL, speedSQL ):
# Collecting All Camera Locations
    redData = many_rows_query( dbConn, redSQL )
    speedData = many_rows_query( dbConn, speedSQL )

    if (len(redData) == 0) & (len(speedData) == 0):
        print("There are no cameras located on that street.")
        print()
        return
    
# Displaying All Camera Locations
    print()
    print("List of Cameras Located on Street:", streetName )
    print("  Red Light Cameras:")
    for row in redData:
        print("    ", row[0], ":", row[1], f"({ row[3] },", f"{row[2]})")

    print("  Speed Cameras:")
    for row in speedData:
        print("    ", row[0], ":", row[1], f"({ row[3] },", f"{row[2]})")
    print()
    plotResponse = input("Plot? (y/n) ")
    print()
    if plotResponse == 'y':
        #
        # populate x and y lists with (x, y) coordinates
        # note that longitude are the X values and
        # latitude are the Y values
        #
        redLabels = []
        redX = []
        redY= []
        speedLabels = []
        speedX = []
        speedY = []
        for row in redData:
            redLabels.append( row[0] )
            redX.append( row[2] )
            redY.append( row[3] )
        for row in speedData:
            speedLabels.append( row[0] )
            speedX.append( row[2] )
            speedY.append( row[3] )
        
        image = plt.imread("chicago.png")
        xydims = [-87.9277, -87.5569, 41.7012, 42.0868] # area covered by the map
        plt.imshow(image, extent=xydims)
        plt.title("Cameras on Street: " + streetName )
        # plt.plot( redX, redY, label )
        # plt.plot( speedX, speedY )
        #
        # annotate each (x, y) coordinate with its station name:
        #
        plt.plot( redX, redY, marker = 'o', markersize = 8, linewidth = 2, color = 'red' )
        plt.plot( speedX, speedY, marker = 'o',  markersize = 8, linewidth = 2, color = 'orange' )
        for row in redData:
            plt.annotate( row[0], xy = (row[2], row[3]) )
        for row in speedData:
            plt.annotate( row[0], xy = (row[2], row[3]))
        plt.xlim([-87.9277, -87.5569])
        plt.ylim([41.7012, 42.0868])
        
        plt.show()
    
##################################################################  
#
# main
#
dbConn = sqlite3.connect('chicago-traffic-cameras.db')

print("Project 1: Chicago Traffic Camera Analysis")
print("CS 341, Spring 2025")
print()
print("This application allows you to analyze various")
print("aspects of the Chicago traffic camera database.")
print()
print_stats(dbConn)
print()

print_menu()

user_input = input("Your choice --> ")
while ( user_input != 'x' ):
    if ( user_input == '1' ): 
        print()
        intersection = input("Enter the name of the intersection to find (wildcards _ and % allowed): ")
        sql = "SELECT Intersection_ID, Intersection FROM Intersections WHERE Intersection LIKE '" + intersection + "' ORDER BY Intersection;"
        option1( dbConn, sql )
    elif ( user_input == '2' ):
        print()
        intersection = input("Enter the name of the intersection (no wildcards allowed): ")
        
        redSQL = "SELECT Camera_ID, Address FROM Intersections as I JOIN RedCameras as R ON I.Intersection_ID = R.Intersection_ID "
        redSQL += "WHERE I.Intersection = '" + intersection + "';"
        speedSQL = "SELECT Camera_ID, Address FROM Intersections as I JOIN SpeedCameras as S ON I.Intersection_ID = S.Intersection_ID "
        speedSQL += "WHERE I.Intersection = '" + intersection + "';"
    
        option2( dbConn, redSQL, speedSQL )
    elif ( user_input == '3' ):
        print()
        
        date = input("Enter the date that you would like to look at (format should be YYYY-MM-DD): " )
        redSQL = "SELECT SUM(Num_Violations) FROM RedViolations WHERE strftime(Violation_Date) = '" + date + "';"
        speedSQL = "SELECT SUM(Num_Violations) FROM SpeedViolations WHERE strftime(Violation_Date) = '" + date + "';"
        
        option3( dbConn, redSQL, speedSQL )
    elif ( user_input == '4' ):
        print()
        redSQL = "SELECT A.Intersection_ID, Intersection, COUNT( DISTINCT B.Camera_ID ) as C FROM Intersections as A JOIN RedCameras as B "
        redSQL += "ON A.Intersection_ID = B.Intersection_ID GROUP BY A.Intersection_ID ORDER BY C DESC, A.Intersection_ID DESC;"
        
        speedSQL = "SELECT A.Intersection_ID, Intersection, COUNT( DISTINCT B.Camera_ID ) as C FROM Intersections as A JOIN SpeedCameras as B "
        speedSQL += "ON A.Intersection_ID = B.Intersection_ID GROUP BY A.Intersection_ID ORDER BY C DESC, A.Intersection_ID DESC;"

        option4( dbConn, redSQL, speedSQL )
    elif ( user_input == '5' ):
        print()
        print()
        year = input("Enter the year that you would like to analyze: " )
        print()
        redSQL = "SELECT A.Intersection, A.Intersection_ID, SUM(C.Num_Violations) as Total FROM Intersections as A "
        redSQL += "JOIN RedCameras as B JOIN RedViolations as C ON A.Intersection_ID = B.Intersection_ID AND B.Camera_ID = C.Camera_ID "
        redSQL += "WHERE strftime('%Y', Violation_Date ) = '" + year + "' GROUP BY A.Intersection_ID ORDER BY Total DESC;"

        speedSQL = "SELECT A.Intersection, A.Intersection_ID, SUM(C.Num_Violations) as Total FROM Intersections as A "
        speedSQL += "JOIN SpeedCameras as B JOIN SpeedViolations as C ON A.Intersection_ID = B.Intersection_ID AND B.Camera_ID = C.Camera_ID "
        speedSQL += "WHERE strftime('%Y', Violation_Date ) = '" + year + "' GROUP BY A.Intersection_ID ORDER BY Total DESC;"

        option5( dbConn, year, redSQL, speedSQL )
    elif ( user_input == '6' ):
        print()
        cameraID = input("Enter a camera ID: ")
        if checkCameraID( dbConn, cameraID ) == 1: 
            redSQL = "SELECT strftime('%Y', Violation_Date) as Year, SUM(Num_Violations) FROM RedCameras as A JOIN RedViolations as B ON A.Camera_ID "
            redSQL += "= B.Camera_ID WHERE A.Camera_ID = " + cameraID + " GROUP BY Year;"

            speedSQL = "SELECT strftime('%Y', Violation_Date) as Year, SUM(Num_Violations) FROM SpeedCameras as A JOIN SpeedViolations as B ON A.Camera_ID "
            speedSQL += "= B.Camera_ID WHERE A.Camera_ID = " + cameraID + " GROUP BY Year;"

            option6( dbConn, cameraID, redSQL, speedSQL )
        else:
            print("No cameras matching that ID were found in the database.")
            print()       
    elif ( user_input == '7' ):
        print()
        cameraID = input("Enter a camera ID: ")
        if checkCameraID( dbConn, cameraID ) == 1: 
            year = input("Enter a year: ")

            redSQL = "SELECT strftime('%m', Violation_Date) as Month, SUM(Num_Violations) FROM RedViolations WHERE Camera_ID = '" + cameraID
            redSQL += "' AND strftime('%Y', Violation_Date ) = '" + year + "' GROUP BY Month;"
            
            speedSQL = "SELECT strftime('%m', Violation_Date) as Month, SUM(Num_Violations) FROM SpeedViolations WHERE Camera_ID = '" + cameraID
            speedSQL += "' AND strftime('%Y', Violation_Date ) = '" + year + "' GROUP BY Month;"
            option7( dbConn, year, cameraID, redSQL, speedSQL )
        else:
            print("No cameras matching that ID were found in the database.")
            print()
    elif ( user_input == '8' ):
        print()
        year = input("Enter a year: ")

        redSQL = "SELECT Date( Violation_Date ) as Date, SUM( Num_Violations ) FROM RedViolations WHERE strftime('%Y', Violation_Date ) = '"
        redSQL += year + "' GROUP BY Date( Violation_Date ) ORDER BY Date( Violation_Date );"
        
        speedSQL= "SELECT Date( Violation_Date ) as Date, SUM( Num_Violations ) FROM SpeedViolations WHERE strftime('%Y', Violation_Date ) = '"
        speedSQL += year + "' GROUP BY Date( Violation_Date ) ORDER BY Date( Violation_Date );"

        option8( dbConn, year, redSQL, speedSQL )
    elif ( user_input == '9' ):
        print()
        streetName = input("Enter a street name: ")
        redSQL = "SELECT Camera_ID, Address, Longitude, Latitude FROM RedCameras WHERE Address LIKE '%" + streetName + "%' ORDER BY Camera_ID;"
        speedSQL = "SELECT Camera_ID, Address, Longitude, Latitude FROM SpeedCameras WHERE Address LIKE '%" + streetName + "%' ORDER BY Camera_ID;"
        
        option9( dbConn, redSQL, speedSQL )
    else:
        print("Error, unknown command, try again...")
        print()

    print_menu()
    user_input = input("Your choice --> ")
    
print("Exiting program.")
#
# done
#