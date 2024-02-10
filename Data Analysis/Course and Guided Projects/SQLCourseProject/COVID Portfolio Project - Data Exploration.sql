--SQL Query for analyzing COVID Data
--Based on a course project

--Select all data from tables and confirm they were imported into database properly
--Adjust data by removing rows where continent value is null

SELECT *
From PortfolioProject..CovidDeaths$
where continent is not null
order by 3,4

--SELECT *
--From PortfolioProject..CovidVaccinations$
--order by 3,4

--Select data to be used for analysis
--then order it by location and date

Select Location, date, total_cases, new_cases, total_deaths, population
From PortfolioProject..CovidDeaths$
where continent is not null
order by 1,2


--Look at total cases vs total deaths
--Query shows likelihood of death if Covid is contracted in a certain country
--Adjust retrieved columns and create new column with alias that calculates death percentage

Select Location, date, total_cases, total_deaths, (total_deaths/total_cases)*100 as DeathPercentage
From PortfolioProject..CovidDeaths$
--Where location like '%states%'
where continent is not null
order by 1,2

-- Looking at total cases vs population
-- shows what percentage of population contracted covid

Select Location, date, Population, total_cases, (total_cases/population)*100 as DeathPercentage
From PortfolioProject..CovidDeaths$
--Where location like '%states%'
where continent is not null
order by 1,2


-- Looking at countries with highest infection rate compared to population

Select Location, Population, MAX(total_cases) as HighestInfectionCount, MAX((total_cases/population))*100 as PercentPopulationInfected
From PortfolioProject..CovidDeaths$
--Where location like '%states%'
where continent is not null
Group by Location, Population
order by PercentPopulationInfected desc


-- Showing countries with highest death count per population
-- casting the total death row to numeric so it can read the max value

Select Location, MAX(cast(total_deaths as int)) as TotalDeathCount
From PortfolioProject..CovidDeaths$
--Where location like '%states%'
where continent is not null
Group by Location
order by TotalDeathCount desc

-- Breaking down data by continent
-- Showing continents with highest death counts

Select location, MAX(cast(total_deaths as int)) as TotalDeathCount
From PortfolioProject..CovidDeaths$
--Where location like '%states%'
where continent is null
Group by location
order by TotalDeathCount desc

Select continent, MAX(cast(total_deaths as int)) as TotalDeathCount
From PortfolioProject..CovidDeaths$
--Where location like '%states%'
where continent is not null
Group by continent
order by TotalDeathCount desc

-- Global Numbers

Select date, SUM(new_cases) as total_cases, SUM(cast(new_deaths as int)) as total_deaths, SUM(cast(new_deaths as int))/SUM(new_cases)*100 as DeathPercentage
From PortfolioProject..CovidDeaths$
--Where location like '%states%'
where continent is not null
Group by date
order by 1,2

-- Looking at total population vs vaccination

Select dea.continent, dea.location, dea.date, dea.population, vac.new_vaccinations, SUM(CONVERT(int, vac.new_vaccinations)) OVER (Partition by dea.Location Order by dea.location, dea.Date) as RollingPeopleVaccinated--, (RollingPeopleVaccinated/population)*100
From PortfolioProject..CovidDeaths$ dea
Join PortfolioProject..CovidVaccinations$ vac
	On dea.location = vac.location
	and dea.date = vac.date
where dea.continent is not null
order by 2,3

--  Use CTE

With PopvsVac (Continent, Location, Date, Population, New_Vaccinations, RollingPeopleVaccinated)
as
(
Select dea.continent, dea.location, dea.date, dea.population, vac.new_vaccinations, SUM(CONVERT(int, vac.new_vaccinations)) OVER (Partition by dea.Location Order by dea.location, dea.Date) as RollingPeopleVaccinated--, (RollingPeopleVaccinated/population)*100
From PortfolioProject..CovidDeaths$ dea
Join PortfolioProject..CovidVaccinations$ vac
	On dea.location = vac.location
	and dea.date = vac.date
where dea.continent is not null
--order by 2,3
)
Select *, (RollingPeopleVaccinated/Population)*100
From PopvsVac


-- Temp Table

Drop Table if exists #PercentPopulationVaccinated
Create Table #PercentPopulationVaccinated
(
Continent nvarchar(255),
Location nvarchar(255),
Date datetime,
Population numeric,
New_vaccinations numeric,
RollingPeopleVaccinated numeric
)

Insert into #PercentPopulationVaccinated
Select dea.continent, dea.location, dea.date, dea.population, vac.new_vaccinations, SUM(CONVERT(int, vac.new_vaccinations)) OVER (Partition by dea.Location Order by dea.location, dea.Date) as RollingPeopleVaccinated--, (RollingPeopleVaccinated/population)*100
From PortfolioProject..CovidDeaths$ dea
Join PortfolioProject..CovidVaccinations$ vac
	On dea.location = vac.location
	and dea.date = vac.date
--where dea.continent is not null
--order by 2,3

Select *, (RollingPeopleVaccinated/Population)*100
From #PercentPopulationVaccinated




-- Creating View to store data for later visualization

Create View PercentPopulationVaccinated as
Select dea.continent, dea.location, dea.date, dea.population, vac.new_vaccinations, SUM(CONVERT(int, vac.new_vaccinations)) OVER (Partition by dea.Location Order by dea.location, dea.Date) as RollingPeopleVaccinated--, (RollingPeopleVaccinated/population)*100
From PortfolioProject..CovidDeaths$ dea
Join PortfolioProject..CovidVaccinations$ vac
	On dea.location = vac.location
	and dea.date = vac.date
where dea.continent is not null
--order by 2,3

Select *
From PercentPopulationVaccinated