// Geometric Tools LLC, Redmond WA 98052
// Copyright (c) 1998-2015
// Distributed under the Boost Software License, Version 1.0.
// http://www.boost.org/LICENSE_1_0.txt
// http://www.geometrictools.com/License/Boost/LICENSE_1_0.txt
// File Version: 1.0.0 (2014/08/11)

#pragma once

#include <gte/GteLogToFile.h>
#include <gte/GteLogToMessageBox.h>
#include <gte/GteLogToOutputWindow.h>
#include <gte/GteLogToStdout.h>
#include <gte/GTEngineDEF.h>

namespace gte
{

class GTE_IMPEXP LogReporter
{
public:
    // Construction and destruction.  Create one of these objects in an
    // application for logging.  The GenerateProject tool creates such code.
    // If you do not want a particular logger, set the flags to
    // LISTEN_FOR_NOTHING and set logFile to "" if you do not want a file.
    ~LogReporter();
    LogReporter(std::string const& logFile, int logFileFlags,
        int logMessageBoxFlags, int logOutputWindowFlags, int logStdoutFlags);

private:
    LogToFile* mLogToFile;
    LogToMessageBox* mLogToMessageBox;
    LogToOutputWindow* mLogToOutputWindow;
    LogToStdout* mLogToStdout;
};

}
