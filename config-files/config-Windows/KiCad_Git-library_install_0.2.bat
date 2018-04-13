@echo off
setlocal enabledelayedexpansion

REM global Variables
SET currentPath=%~dp0
set userKiCadPath=%userprofile%\AppData\Roaming\kicad
set gitKiCadPath=%currentPath:~0,-1%
set relPathToTopLevelGit=..\..\
pushd %relPathToTopLevelGit%
set absPathToTopLevelGit=%CD%
popd

echo Checking kicad_common

REM This script adapts the [EnvironmentVariables] of the kicad_common file of the local Kicad
REM installation to the path of the Kicad libraries by parsing the kicad_common file provided
REM with the GIT libraries.
REM It parses the files fp-lib-table and sym-lib-table (both INSTALL) and appends the lines from
REM the corresponding files from the GIT folder only when those lines are not found in the files
REM It needs to be run from the first level inside the GIT Kicad folder

REM Check if kicad_common exists in ..\config-files\config-Windows
REM Read contents of kicad_common in the GIT-Directory into Array "fileKicadCommonGit"
REM Variables | "fileKicadCommonGit[]" = All lines of the kicad_common file (GIT)
if exist %gitKiCadPath%\kicad_common (
	set i=0
	FOR /F "tokens=1 delims=" %%a in (%gitKiCadPath%\kicad_common) do (
		set fileKicadCommonGit[!i!]=%%a
		set /a i+=1
	)
) else (
	echo.
	echo File kicad_common not found in %gitKiCadPath%
	GOTO end_l
)

REM Check if kicad_common exists in USERDIRECTORY\AppData\Roaming\kicad
REM Read contents of kicad_common in the INSTALL directory into Array "fileKicadCommonInstall"
REM Variables | "fileKicadCommonInstall[]" = All lines of the kicad_common file (INSTALL)
if exist %userKiCadPath%\kicad_common (
	set j=0
	FOR /F "tokens=1 delims=" %%b in (%userKiCadPath%\kicad_common) do (
		set fileKicadCommonInstall[!j!]=%%b
		set /a j+=1
	)
) else (
	echo.
	echo File kicad_common not found in %userKiCadPath%
	GOTO end_l
)

REM Variables |	"linesToChange[]" = Lines in which the Path needs to be replaced i.e file system paths
REM 		  |	"linesNotToChange[]" = Lines which are written to the output file unchanged i.e. 
REM									 URLs
REM ---------------------------------
REM Parse contents of Array "fileKicadCommonGit" into Array "linesToChange"
set environmentVariablesBool= 0
set k=0
set l=0
set /A i-=1
for /l %%c in (0,1,%i%) do (
	REM parses all lines of GIT kicad_common file and sorts the lines after the [ENVIRONMENT VARIABLES]
	REM it into two arrays. "linesToChange" and "linesNotToChange"
	REM The Variable "KIGITHUB" is exlcuded since it is a URL
	if !environmentVariablesBool!==1 if NOT "!fileKicadCommonGit[%%c]:~0,8!"=="KIGITHUB" ( 
		set linesToChange[!k!]=!fileKicadCommonGit[%%c]!
		set /a k+=1
	) else (
		if !environmentVariablesBool!==1 if "!fileKicadCommonGit[%%c]:~0,8!"=="KIGITHUB" (
			set linesNotToChange[!l!]=!fileKicadCommonGit[%%c]!
			set /a l+=1
		)
	)
	
	if "!fileKicadCommonGit[%%c]!"=="[EnvironmentVariables]" ( set /A environmentVariablesBool= 1)
)

REM Writes the unaltered lines of kicad_common file (INSTALL) from the first line to the 
REM [ENVIRONMENT VARIABLES] tag to new kicad_common file
set firstLineBool=0
set finishedAtEnvironmentVariables=0
set /A j-=1
for /l %%d in (0,1,%j%) do (
	if "!fileKicadCommonInstall[%%d]: =!"=="[EnvironmentVariables]" (
		set /A finishedAtEnvironmentVariables=1
		echo !fileKicadCommonInstall[%%d]!>> !userKiCadPath!\kicad_common
	)
	if !finishedAtEnvironmentVariables!==0 (
		if !firstLineBool!==1 (
			echo !fileKicadCommonInstall[%%d]!>> !userKiCadPath!\kicad_common
		)
		if !firstLineBool!==0 (
			REM This line with the ">"-operator actually overwrites the old file
			echo !fileKicadCommonInstall[%%d]!> !userKiCadPath!\kicad_common
			set /A firstLineBool=1
		)
	)	
)

REM Alters the paths of each [EnvironmentVariables] from "linesToChange" and appends the them
REM to the new kicad_common file. Paths with forward slashes and paths with backward slashes
REM are distinguished and processed seperatly.
set /a k-=1
for /l %%e in (0,1,%k%) do (
	for /f "tokens=1,2 delims=:" %%A in ("!linesToChange[%%e]!") do (
		set environmentVariableName=%%A
		set url=%%B
		if "!url:~0,1!"=="/" (
			set linesToChange[%%e]=!environmentVariableName:~0,-1!!absPathToTopLevelGit:\\=//!!url:~7!
		)
		if "!url:~0,1!"=="\" (
			set linesToChange[%%e]=!environmentVariableName:~0,-1!!absPathToTopLevelGit:\=\\!!url:~7!
		)
		
		echo !linesToChange[%%e]!>> !userKiCadPath!\kicad_common
	)
)

REM Appends the "linesNotToChange" to the new kicad_common file.
set /a l-=1
for /l %%f in (0,1,%l%) do (
	echo !linesNotToChange[%%f]!>> !userKiCadPath!\kicad_common
)

REM stats as to how many lines had been altered
echo stats:
set /A k+=1
set /A l+=1
set /A numEnvVar=%k%+%l%
echo Number of [ENVIRONMENT VARIABLES] read from kicad_common file (GIT): %numEnvVar%
echo Number of altered [ENVIRONMENT VARIABLES]:  %k%
echo Number of unaltered [ENVIRONMENT VARIABLES]:  %l%
echo.

REM ---------------------------------------------------------------
REM Check if fp-lib-table exists in ..\config-files\config-Windows
REM Read lines of fp-lib-table from the GIT-Directory into array fileFpLibTable
REM Variables | "fileFpLibTableGit" = All lines from the fp-lib-table file (GIT)
echo Checking fp-lib-table:
if exist %gitKiCadPath%\fp-lib-table (
	set m=0
	for /F "tokens=1 delims=" %%g in (%gitKiCadPath%\fp-lib-table) do (
		set fileFpLibTableGit[!m!]=%%g
		set /a m+=1
	)
) else (
	echo.
	echo File fp-lib-table not found in %gitKiCadPath%
	GOTO end_l
)

REM Check if fp-lib-table exists in USERDIRECTORY\AppData\Roaming\kicad
REM Read lines of fp-lib-table from the INSTALL-Directory into array fileFpLibTableInstall
REM Variables | "fileFpLibTableInstall" = All lines from the fp-lib-table file (INSTALL)
if exist %userKiCadPath%\fp-lib-table (
	set n=0
	for /F "tokens=1 delims=" %%h in (%userKiCadPath%\fp-lib-table) do (
		set fileFpLibTableInstall[!n!]=%%h
		set /a n+=1
	)
) else (
	echo.
	echo File fp-lib-table not found in %userKiCadPath%
	GOTO end_l
)

REM Compares the lines of the fp-lib-table files (GIT & INSTALL) and stores the lines
REM from the GIT file which need to be appended to the INSTALL file in "toAppend"
REM Variables | "toAppend" = Lines which need to be appended to fp-lib-table (INSTALL)
set /a m-=2
set /a n-=1
set matchBool=0
set matchesFpLibTable=0
set appendedFpLibTable=0
for /l %%z in (1,1,%m%) do (
	for /l %%y in (0,1,%n%) do (
		if "!fileFpLibTableGit[%%z]: =!"=="!fileFpLibTableInstall[%%y]: =!" (
			set /A matchBool=1
		)		
	)
	if !matchBool!==0 (
		set toAppend[!appendedFpLibTable!]=!fileFpLibTableGit[%%z]!
		set /A appendedFpLibTable+=1
	) else (
		set /A matchesFpLibTable+=1
	)
	set /A matchBool=0	
)

REM This line with the ">"-operator actually overwrites the old file
echo (fp_lib_table> %userKiCadPath%\fp-lib-table

REM Writes the already existing lines back to the new fp-lib-table file
set /A n-=1
for /L %%x in (1,1,%n%) do (
	echo !fileFpLibTableInstall[%%x]!>> %userKiCadPath%\fp-lib-table
)

REM Appends to the line from "toAppend" to the new fp-lib-table file
set /A appendedFpLibTable-=1
for /L %%w in (0,1,%appendedFpLibTable%) do (
	echo !toAppend[%%w]!>> %userKiCadPath%\fp-lib-table
)
echo )>> %userKiCadPath%\fp-lib-table

REM stats as to how many lines have been found in each file and how many lines
REM from the fp-lib-table (GIT) have been found in the fp-lib-table (INSTALL) and
REM how many were appended
set /A appendedFpLibTable +=1
echo stats:
echo Number of entries read from fp-lib-table (GIT): %m%
echo Number of entries read from fp-lib-table (INSTALL): %n%
echo Matches found in fp-lib-tables: %matchesFpLibTable%
echo Number of lines appended to fp-lib-table (From GIT to INSTALL): %appendedFpLibTable%
echo.


REM ---------------------------------------------------------------
REM Check if sym-lib-table exists in ..\config-files\config-Windows
REM Read lines of sym-lib-table from the GIT-Directory into array fileSymLibTable
REM Variables | "fileSymLibTableGit" = All lines from the sym-lib-table file (GIT)
echo Checking sym-lib-table:
if exist %gitKiCadPath%\sym-lib-table (
	set m=0
	for /F "tokens=1 delims=" %%g in (%gitKiCadPath%\sym-lib-table) do (
		set fileSymLibTableGit[!m!]=%%g
		set /a m+=1
	)
) else (
	echo.
	echo File sym-lib-table not found in %gitKiCadPath%
	GOTO end_l
)

REM Check if sym-lib-table exists in USERDIRECTORY\AppData\Roaming\kicad
REM Read lines of sym-lib-table from the INSTALL-Directory into array fileSymLibTableInstall
REM Variables | "fileSymLibTableInstall" = All lines from the sym-lib-table file (INSTALL)
if exist %userKiCadPath%\sym-lib-table (
	set n=0
	for /F "tokens=1 delims=" %%h in (%userKiCadPath%\sym-lib-table) do (
		set fileSymLibTableInstall[!n!]=%%h
		set /a n+=1
	)
) else (
	echo.
	echo File sym-lib-table not found in %userKiCadPath%
	GOTO end_l
)

REM Compares the lines of the sym-lib-table files (GIT & INSTALL) and stores the lines
REM from the GIT file which need to be appended to the INSTALL file in "toAppend"
REM Variables | "toAppend" = Lines which need to be appended to sym-lib-table (INSTALL)
set /a m-=2
set /a n-=1
set matchBool=0
set matchesSymLibTable=0
set appendedSymLibTable=0
for /l %%z in (1,1,%m%) do (
	for /l %%y in (0,1,%n%) do (
		if "!fileSymLibTableGit[%%z]: =!"=="!fileSymLibTableInstall[%%y]: =!" (
			set /A matchBool=1
		)		
	)
	if !matchBool!==0 (
		set toAppend[!appendedSymLibTable!]=!fileSymLibTableGit[%%z]!
		set /A appendedSymLibTable+=1
	) else (
		set /A matchesSymLibTable+=1
	)
	set /A matchBool=0	
)

REM This line with the ">"-operator actually overwrites the old file
echo (sym_lib_table> %userKiCadPath%\sym-lib-table

REM Writes the already existing lines back to the new sym-lib-table file
set /A n-=1
for /L %%x in (1,1,%n%) do (
	echo !fileSymLibTableInstall[%%x]!>> %userKiCadPath%\sym-lib-table
)

REM Appends to the line from "toAppend" to the new sym-lib-table file
set /A appendedSymLibTable-=1
for /L %%w in (0,1,%appendedSymLibTable%) do (
	echo !toAppend[%%w]!>> %userKiCadPath%\sym-lib-table
)
echo )>> %userKiCadPath%\sym-lib-table


REM stats as to how many lines have been found in each file and how many lines
REM from the fp-lib-table (GIT) have been found in the fp-lib-table (INSTALL) and
REM how many were appended
set /A appendedSymLibTable +=1
echo stats:
echo Number of entries read from sym-lib-table (GIT): %m%
echo Number of entries read from sym-lib-table (INSTALL): %n%
echo Matches found in sym-lib-tables: %matchesSymLibTable%
echo Number of lines appended to sym-lib-table (From GIT to INSTALL): %appendedSymLibTable%
echo.
echo.
echo Done^^! :)
echo.
echo.

GOTO finish
:end_l
echo.
echo Please check location of the files (.batch, kicad_common, fp-lib-table, sym-lib-table)
echo in both the GIT and the INSTALL-Directory
echo.
echo.

:finish
echo Beliebige Taste zum Beenden druecken.
PAUSE >nul