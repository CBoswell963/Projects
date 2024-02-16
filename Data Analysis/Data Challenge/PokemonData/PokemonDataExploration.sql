/*
	Confirming data was imported properly
*/

SELECT TOP (1000) [abilities]
      ,[against_bug]
      ,[against_dark]
      ,[against_dragon]
      ,[against_electric]
      ,[against_fairy]
      ,[against_fight]
      ,[against_fire]
      ,[against_flying]
      ,[against_ghost]
      ,[against_grass]
      ,[against_ground]
      ,[against_ice]
      ,[against_normal]
      ,[against_poison]
      ,[against_psychic]
      ,[against_rock]
      ,[against_steel]
      ,[against_water]
      ,[attack]
      ,[base_egg_steps]
      ,[base_happiness]
      ,[base_total]
      ,[capture_rate]
      ,[classfication]
      ,[defense]
      ,[experience_growth]
      ,[height_m]
      ,[hp]
      ,[japanese_name]
      ,[name]
      ,[percentage_male]
      ,[pokedex_number]
      ,[sp_attack]
      ,[sp_defense]
      ,[speed]
      ,[type1]
      ,[type2]
      ,[weight_kg]
      ,[generation]
      ,[is_legendary]
  FROM [PokemonData].[dbo].[pokemon$]

  --Check pokemon names column

  SELECT name
  FROM PokemonData.dbo.pokemon$

  --Look at table with basic pokemon information alongside their japanese names

  Select cast(pokedex_number as int), name, japanese_name, type1, type2
  FROM PokemonData.dbo.pokemon$
  order by 1


  -- Separate pokemon by region


  --Kanto Region
  SELECT cast(pokedex_number as int), name, japanese_name, type1, type2
  FROM PokemonData.dbo.pokemon$
  WHERE cast(pokedex_number as int) BETWEEN 1 AND 151

  --Johto Region
  SELECT cast(pokedex_number as int), name, japanese_name, type1, type2
  FROM PokemonData.dbo.pokemon$
  WHERE cast(pokedex_number as int) BETWEEN 152 AND 251

  --Hoenn Region
  SELECT cast(pokedex_number as int), name, japanese_name, type1, type2
  FROM PokemonData.dbo.pokemon$
  WHERE cast(pokedex_number as int) BETWEEN 252 AND 386

  --Sinnoh Region
  SELECT cast(pokedex_number as int), name, japanese_name, type1, type2
  FROM PokemonData.dbo.pokemon$
  WHERE cast(pokedex_number as int) BETWEEN 387 AND 493

   --Unova Region
  SELECT cast(pokedex_number as int), name, japanese_name, type1, type2
  FROM PokemonData.dbo.pokemon$
  WHERE cast(pokedex_number as int) BETWEEN 494 AND 649

  --Kalos Region
  SELECT cast(pokedex_number as int), name, japanese_name, type1, type2
  FROM PokemonData.dbo.pokemon$
  WHERE cast(pokedex_number as int) BETWEEN 650 AND 721

  --Alola Region
  SELECT cast(pokedex_number as int), name, japanese_name, type1, type2
  FROM PokemonData.dbo.pokemon$
  WHERE cast(pokedex_number as int) BETWEEN 722 AND 809