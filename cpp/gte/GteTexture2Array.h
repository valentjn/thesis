// Geometric Tools LLC, Redmond WA 98052
// Copyright (c) 1998-2015
// Distributed under the Boost Software License, Version 1.0.
// http://www.boost.org/LICENSE_1_0.txt
// http://www.geometrictools.com/License/Boost/LICENSE_1_0.txt
// File Version: 1.0.0 (2014/08/11)

#pragma once

#include <gte/GteTextureArray.h>
#include <gte/GTEngineDEF.h>

namespace gte
{

class GTE_IMPEXP Texture2Array : public TextureArray
{
public:
    // Construction.
    Texture2Array(unsigned int numItems, DFType format, unsigned int width,
        unsigned int height, bool hasMipmaps = false,
        bool createStorage = true);

    // Texture dimensions.
    unsigned int GetWidth() const;
    unsigned int GetHeight() const;
};

}
