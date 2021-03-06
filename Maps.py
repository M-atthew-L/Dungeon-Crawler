class UniqueRooms():

    #---------------------------------------------------------------------------------------------------------------------------------------

    STARTING_ROOM = ["-----------------------------------------------------------------",
                     "|    H                    V  C  T          X                    |",
                     "|                                                               |",
                     "|----------                                           ----------|",
                     "|        M         |     ----       ----     |                  |",
                     "|                  |     |             |     |          B       |",
                     "| !      !      !  |     |             |     |                  |",
                     "|                  |  A  |      H      |  A  |                  |",
                     "-----------------------------------------------------------------"]

    #---------------------------------------------------------------------------------------------------------------------------------------

    ROOM_ONE = ["-------------------------------------------------",
                "|            |                  |         |/////|",
                "|            |                  |         |/////|",
                "|            |        ---                 ------|",
                "|                                               |",
                "|                      -----            |       |",
                "|---------                 |    ---     |       |",
                "|                          |            |      H|",
                "-------------------------------------------------"]

    ROOM_TWO = ["-------------------------------------------------",
                "|              |            |                   |",
                "|------        |            |            -------|",
                "|              |                         |      |",
                "|              |                                |",
                "|            -----          ---          |      |",
                "|---                         |           |      |",
                "|                            |           |     H|",
                "-------------------------------------------------"]

    ROOM_THREE = ["-------------------------------------------------",
                  "|                                       |       |",
                  "|       |            |             -----|       |",
                  "|    ---|            |                          |",
                  "|               -----|-----                     |",
                  "|------              |              |           |",
                  "|/////|              |              |           |",
                  "|/////|                             |          H|",
                  "-------------------------------------------------"]
 
    ROOM_FOUR = ["--------------------------------------------------",
                 "|                                |               |",
                 "|                /               |               |",
                 "|----           /                            ----|",
                 "|              /        -----                    |",
                 "|    -        /                      -----       |",
                 "|   |/|                  |           |           |",
                 "|    -                   |                      H|",
                 "--------------------------------------------------"]
 
    ROOM_FIVE = ["-----------------------------------|//////////////",
                 "|    |                 |           |//////////////",
                 "|    |                 |           |//////////////",
                 "|    |-----                        --------------|",
                 "|                        -----                   |",
                 "|             |                           -------|",
                 "|------       |-------          |                |",
                 "|             |                 |               H|",
                 "--------------------------------------------------"]

    ROOM_SIX = ["---------------------------------------------//////",
                "|            |                  |           |//////",
                "|            |                  |           |//////",
                "|            |        ---                   ------|",
                "|                                                 |",
                "|                      -----             |        |",
                "|---------                 |     ---     |        |",
                "|                          |             |       H|",
                "---------------------------------------------------"]

    ROOM_SEVEN = ["-------------------------",
                  "|        |      |       |",
                  "|        |    --|       |",
                  "|        |          ----|",
                  "|    ----|----          |",
                  "|                ----   |",
                  "|----      |     |      |",
                  "|          |           H|",
                  "-------------------------"]

    ROOM_EIGHT = ["---------------------------------------",
                  "|              |                      |",
                  "|              |     -----     -------|",
                  "|    ----      |     |      ___|      |",
                  "|                    |      |         |",
                  "|       |            |               H|",
                  "---------------------------------------"]

    ROOM_NINE = ["-------------------",
                 "|                 |",
                 "|        |        |",
                 "|     -------     |",
                 "|        |        |",
                 "|                H|",
                 "-------------------"]

    ROOM_TEN = ["-------------------------",
                "|                       |",
                "|        /    /    /    |",
                "|       /    /    /     |",
                "|      /    /    /      |",
                "|                      H|",
                "-------------------------"]

    ROOM_ELEVEN = ["-------------------------------------",
                   "|            |                  | $ |",
                   "|            |        -----     |   |",
                   "|            |          |       |   |",
                   "|                                   |",
                   "|----                   |           |",
                   "|$ d   |   ---|      -------        |",
                   "|$ $ c |     $|           $|       H|",
                   "-------------------------------------"]
    
    ROOM_TWELVE = ["-----------------------------",
                   "|    |        $|            |",
                   "|    |         |        ----|",
                   "|    |    -----|-----   |   |",
                   "|    |              |       |",
                   "|    |-----                 |",
                   "|                    ---    |",
                   "|          -----     |z|    |",
                   "|--------      |     ---    |",
                   "|$             |           H|",
                   "-----------------------------"]

    ROOM_THIRTEEN = ["-----------------------------------------------",
                     "|                    -------  $ |             |",
                     "|-------   ------          |    |             |",
                     "| d  $$|     |          ---|    |    -----    |",
                     "|  ----|     |-----           -----      |    |",
                     "|    c        z  $|    |                 |   H|",
                     "-----------------------------------------------"] 

    ROOM_FOURTEEN = ["-----------------------",
                     "|               |     |",
                     "|               |     |",
                     "|----      ------     |",
                     "|          |          |",
                     "|      -----   -------|",
                     "|                 |   |",
                     "|------           |   |",
                     "|     |         ----- |",
                     "|     ----            |",
                     "|        |      |     |",
                     "|               |    H|",
                     "-----------------------"]

    ROOM_FIFTEEN = ["-----------------------------------",
                    "|                                 |",
                    "|    \\  -----   |   -----    /   |",
                    "|     \\         |           /    |",
                    "|  |   \\                   /  |  |",
                    "|       \\     -----       /      |",
                    "|       /      |///|      \\      |",
                    "|  |   /       -----       \\  |  |",
                    "|     /                     \\    |",
                    "|    /           |           \\   |",
                    "|        -----   |   -----        |",
                    "|                                H|",
                    "----------------------------------"]
    #---------------------------------------------------------------------------------------------------------------------------------------

    ROOM_MERCHANT = ["-------------------",
                     "|                 |",
                     "|        M        |",
                     "|                 |",
                     "|    !   !   !    |",
                     "|                H|",
                     "-------------------"]

    ROOM_MYSTERYMAN = ["-----------",
                       "|         |",
                       "|    ?    |",
                       "|        H|",
                       "-----------"]

    #---------------------------------------------------------------------------------------------------------------------------------------


    ROOMS = [ROOM_ONE, ROOM_TWO, ROOM_THREE, ROOM_FOUR, ROOM_FIVE, ROOM_SIX, ROOM_MERCHANT, ROOM_MYSTERYMAN]