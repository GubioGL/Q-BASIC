@ECHO OFF
REM Atalhos do Sphinx no Windows. Uso: make.bat html
pushd %~dp0
if "%SPHINXBUILD%" == "" set SPHINXBUILD=python -m sphinx
set SOURCEDIR=source
set BUILDDIR=_build
if "%1" == "" goto help
%SPHINXBUILD% -M %1 %SOURCEDIR% %BUILDDIR% -W --keep-going %SPHINXOPTS%
goto end
:help
%SPHINXBUILD% -M help %SOURCEDIR% %BUILDDIR% %SPHINXOPTS%
:end
popd
