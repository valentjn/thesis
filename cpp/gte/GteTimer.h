// Geometric Tools LLC, Redmond WA 98052
// Copyright (c) 1998-2015
// Distributed under the Boost Software License, Version 1.0.
// http://www.boost.org/LICENSE_1_0.txt
// http://www.geometrictools.com/License/Boost/LICENSE_1_0.txt
// File Version: 1.0.0 (2014/08/11)

#pragma once

#include <gte/GTEngineDEF.h>
#include <cstdint>

namespace gte
{

class GTE_IMPEXP Timer
{
public:
    // Construction of a high-resolution timer (64-bit).
    Timer();

    // Get the current ticks or time relative to the initial time.
    int64_t GetTicks();
    double GetSeconds();

    // Get the time for the specified number of ticks.
    double GetSeconds(int64_t numTicks) const;

    // Get the number of ticks for the specified time.
    int64_t GetTicks(double seconds) const;

    // Reset so that initial ticks is the current time.
    void Reset();

private:
    int64_t mFrequency;
    int64_t mInitialTicks;
    double mInvFrequency;
};

}
