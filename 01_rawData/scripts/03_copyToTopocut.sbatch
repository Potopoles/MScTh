#!/bin/bash -l
#
#SBATCH --job-name="copyToTopocut"
#SBATCH --time=18:00:00
#SBATCH --ntasks=1
#SBATCH --account='pr04'
#SBATCH --partition=xfer
#SBATCH --output=bOut/sbatch.out
#SBATCH --error=bOut/sbatch.err


rm ../topocut/4.4/*
rm ../topocut/4.4f/*
rm ../topocut/2.2/*
rm ../topocut/2.2f/*
rm ../topocut/1.1/*
rm ../topocut/1.1f/*

cp ../4.4/lffd200607*z.nc ../topocut/4.4/
cp ../4.4f/lffd200607*z.nc ../topocut/4.4f/
cp ../2.2/lffd200607*z.nc ../topocut/2.2/
cp ../2.2f/lffd200607*z.nc ../topocut/2.2f/
cp ../1.1/lffd200607*z.nc ../topocut/1.1/
cp ../1.1f/lffd200607*z.nc ../topocut/1.1f/

