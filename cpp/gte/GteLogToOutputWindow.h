// Geometric Tools LLC, Redmond WA 98052
// Copyright (c) 1998-2015
// Distributed under the Boost Software License, Version 1.0.
// http://www.boost.org/LICENSE_1_0.txt
// http://www.geometrictools.com/License/Boost/LICENSE_1_0.txt
// File Version: 1.0.0 (2014/08/11)

#pragma once

#include <gte/GteLogger.h>

namespace gte
{

class GTE_IMPEXP LogToOutputWindow : public Logger::Listener
{
public:
    LogToOutputWindow(int flags);

private:
    virtual void Report(std::string const& message);
};

}
