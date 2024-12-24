-- Total MidRange Shots >= 5

SELECT 
    Player,
	Team,
    SUM(TotalMidRangeShots) AS TotalMidRangeShots,
    SUM(TotalMidRangeMakes) AS TotalMidRangeMakes,
    (SUM(TotalMidRangeMakes) / NULLIF(SUM(TotalMidRangeShots), 0)) * 100 AS "MidRange%"
FROM (
    SELECT 
        PrimaryPlayer AS Player,
        OffensivePossession AS Team,
        SUM(CASE WHEN ShotLevel IN (2, 3) THEN 1 ELSE 0 END) AS TotalMidRangeShots,
        SUM(CASE WHEN (ShotLevel IN (2, 3) AND Outcome IN ('And1', '2pMa')) THEN 1 ELSE 0 END) AS TotalMidRangeMakes
    FROM plays
    WHERE 
        SecondaryPlayer = 'N/A'  AND -- Add'AND clause with playnumbers for specific playtypes for play type efficiency
		OffensivePossession IN ('Bard College', 'Clarkson University Golden Knights', 'Rensselaer Polytechnic', 
							   'Rochester Institute of Technology Tigers', 'Skidmore Thoroughbreds', 'Vassar Brewers', 
							   'Hobart College Statesmen', 'Ithaca College', 'Union (NY) Chargers', 'St. Lawrence Saints')

    GROUP BY 
        PrimaryPlayer,
        OffensivePossession
    
    UNION ALL
    
    SELECT 
        SecondaryPlayer AS Player,
        OffensivePossession AS Team,
        SUM(CASE WHEN ShotLevel IN (2, 3) THEN 1 ELSE 0 END) AS TotalMidRangeShots,
        SUM(CASE WHEN (ShotLevel IN (2, 3) AND Outcome IN ('And1', '2pMa')) THEN 1 ELSE 0 END) AS TotalMidRangeMakes
    FROM plays
    WHERE 
        SecondaryPlayer <> 'N/A' AND -- Add'AND clause with playnumbers for specific playtypes for play type efficiency
		OffensivePossession IN ('Bard College', 'Clarkson University Golden Knights', 'Rensselaer Polytechnic', 
							   'Rochester Institute of Technology Tigers', 'Skidmore Thoroughbreds', 'Vassar Brewers', 
							   'Hobart College Statesmen', 'Ithaca College', 'Union (NY) Chargers', 'St. Lawrence Saints')

    GROUP BY 
        SecondaryPlayer,
        OffensivePossession
) AS CombinedStats
WHERE 
	TotalMidRangeShots >= 5
GROUP BY 
    Player, Team
ORDER BY 
    TotalMidRangeShots DESC;