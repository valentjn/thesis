function execute(command)
  local i, j = io.popen(command)
  if not i then
    print(j)
    os.exit(-1)
  end
  tex.sprint(-2, i:read("*all"))
  i:close()
end

function getGitCommitHash()
  execute("git log -1 --pretty=format:%h")
end

function getGitCommitTimeShort()
  execute("LC_ALL=en_US git log -1 --pretty=format:%cd '--date=format:%b %d, %l:%M%P'")
end

function getGitCommitTimeLong()
  execute("LC_ALL=en_US git log -1 --pretty=format:%cd '--date=format:%B %e, %Y at %l:%M%P'")
end

function getCurrentTimeShort()
  execute("LC_ALL=en_US date '+%b %d, %l:%M%P' | tr -d '\n'")
end

function getCurrentTimeLong()
  execute("LC_ALL=en_US date '+%B %e, %Y at %l:%M%P' | tr -d '\n'")
end

function getAndIncreaseCompileCounter()
  f = io.open("../../compile_counter.txt", "r")
  local counter = f:read("*n")
  f:close()
  
  counter = tostring(counter + 1)
  
  f = io.open("../../compile_counter.txt", "w+")
  f:write(counter .. "\n")
  f:close()
  
  tex.print(counter)
end
