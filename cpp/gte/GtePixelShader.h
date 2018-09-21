// Geometric Tools LLC, Redmond WA 98052
// Copyright (c) 1998-2015
// Distributed under the Boost Software License, Version 1.0.
// http://www.boost.org/LICENSE_1_0.txt
// http://www.geometrictools.com/License/Boost/LICENSE_1_0.txt
// File Version: 1.0.0 (2014/08/11)

#pragma once

#include <gte/GteShader.h>
#include <gte/GTEngineDEF.h>

namespace gte
{

class GTE_IMPEXP PixelShader : public Shader
{
public:
    // Construction.
    PixelShader (HLSLShader const& program);
};

}
