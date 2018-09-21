// Geometric Tools LLC, Redmond WA 98052
// Copyright (c) 1998-2015
// Distributed under the Boost Software License, Version 1.0.
// http://www.boost.org/LICENSE_1_0.txt
// http://www.geometrictools.com/License/Boost/LICENSE_1_0.txt
// File Version: 1.0.1 (2014/08/31)

#pragma once

#include <gte/GteHLSLResource.h>
#include <gte/GteHLSLShaderType.h>
#include <gte/GteHLSLShaderVariable.h>
#include <gte/GteMemberLayout.h>
#include <gte/GTEngineDEF.h>
#include <fstream>

namespace gte
{

class GTE_IMPEXP HLSLBaseBuffer : public HLSLResource
{
public:
    typedef std::pair<HLSLShaderVariable, HLSLShaderType> Member;

    // Construction and destruction.
    virtual ~HLSLBaseBuffer();

    HLSLBaseBuffer(D3D11_SHADER_INPUT_BIND_DESC const& desc,
        unsigned int numBytes, std::vector<Member> const& members);

    HLSLBaseBuffer(D3D11_SHADER_INPUT_BIND_DESC const& desc,
        unsigned int index, unsigned int numBytes,
        std::vector<Member> const& members);

    // Member access.
    std::vector<Member> const& GetMembers() const;

    // Print to a text file for human readability.
    virtual void Print(std::ofstream& output) const;

    // Generation of lookup tables for member layout.
    void GenerateLayout(std::vector<MemberLayout>& layout) const;

private:
    void GenerateLayout(HLSLShaderType const& type, unsigned int parentOffset,
        std::string const& parentName,
        std::vector<MemberLayout>& layout) const;

    std::vector<Member> mMembers;
};

}
