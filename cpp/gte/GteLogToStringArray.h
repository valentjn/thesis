// Geometric Tools LLC, Redmond WA 98052
// Copyright (c) 1998-2015
// Distributed under the Boost Software License, Version 1.0.
// http://www.boost.org/LICENSE_1_0.txt
// http://www.geometrictools.com/License/Boost/LICENSE_1_0.txt
// File Version: 1.0.0 (2014/08/11)

#pragma once

#include <gte/GteLogger.h>
#include <gte/GTEngineDEF.h>
#include <vector>

namespace gte
{

class GTE_IMPEXP LogToStringArray : public Logger::Listener
{
public:
    LogToStringArray(std::string const& name, int flags);

    std::string const& GetName() const;
    std::vector<std::string> const& GetMessages() const;
    std::vector<std::string>& GetMessages();

private:
    virtual void Report(std::string const& message);

    std::string mName;
    std::vector<std::string> mMessages;
};

}
