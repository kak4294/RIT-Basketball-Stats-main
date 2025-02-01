SELECT 
    Team, 
    PlayType, 
    ThreePM, 
    ThreePA, 
    Percentage AS Percent
FROM 
    (
    SELECT 
        Team,
        'Pick-and-Roll' AS PlayType,
        SUM(O_Pnr3PM) AS ThreePM,
        SUM(O_Pnr3PA) AS ThreePA,
        ROUND((SUM(O_Pnr3PM) / NULLIF(SUM(O_Pnr3PA), 0)) * 100, 2) AS Percentage
    FROM TeamGames
    GROUP BY Team

    UNION ALL

    SELECT
        Team,
        'Roll' AS PlayType,
        SUM(O_Roll3PM) AS ThreePM,
        SUM(O_Roll3PA) AS ThreePA,
        ROUND((SUM(O_Roll3PM) / NULLIF(SUM(O_Roll3PA), 0)) * 100, 2) AS Percentage
    FROM TeamGames
    GROUP BY Team

    UNION ALL

    SELECT
        Team,
        'Spot Up Shots' AS PlayType,
        SUM(O_SUShot3PM) AS ThreePM,
        SUM(O_SUShot3PA) AS ThreePA,
        ROUND((SUM(O_SUShot3PM) / NULLIF(SUM(O_SUShot3PA), 0)) * 100, 2) AS Percentage
    FROM TeamGames
    GROUP BY Team

    UNION ALL

    SELECT
        Team,
        'Isolation' AS PlayType,
        SUM(O_Iso3PM) AS ThreePM,
        SUM(O_Iso3PA) AS ThreePA,
        ROUND((SUM(O_Iso3PM) / NULLIF(SUM(O_Iso3PA), 0)) * 100, 2) AS Percentage
    FROM TeamGames
    GROUP BY Team

    UNION ALL

    SELECT
        Team,
        'Transition' AS PlayType,
        SUM(O_Transition3PM) AS ThreePM,
        SUM(O_Transition3PA) AS ThreePA,
        ROUND((SUM(O_Transition3PM) / NULLIF(SUM(O_Transition3PA), 0)) * 100, 2) AS Percentage
    FROM TeamGames
    GROUP BY Team

    UNION ALL

    SELECT 
        Team,
        'Hand Offs' AS PlayType,
        SUM(O_HaOf3PM) AS ThreePM,
        SUM(O_HaOf3PA) AS ThreePA,
        ROUND((SUM(O_HaOf3PM) / NULLIF(SUM(O_HaOf3PA), 0)) * 100, 2) AS Percentage
    FROM TeamGames
    GROUP BY Team

    UNION ALL

    SELECT 
        Team,
        'Ofsc' AS PlayType,
        SUM(O_Ofsc3PM) AS ThreePM,
        SUM(O_Ofsc3PA) AS ThreePA,
        ROUND((SUM(O_Ofsc3PM) / NULLIF(SUM(O_Ofsc3PA), 0)) * 100, 2) AS Percentage
    FROM TeamGames
    GROUP BY Team
    ) AS pivoted_data
WHERE
    Team IN (
        "Bard College", 
        "Clarkson University Golden Knights", 
        "Hobart College Statesmen",
        "Ithaca College",
        "Rensselaer Polytechnic",
        "Rochester Institute of Technology Tigers",
        "Skidmore Thoroughbreds",
        "St. Lawrence Saints",
        "Union (NY) Chargers",
        "Vassar Brewers"
    )
ORDER BY
    Team, PlayType;
