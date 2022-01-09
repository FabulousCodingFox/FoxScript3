log info Start
log warn Warning
log debug Debug

execute run function {
    log info This is executed in another function
    execute run function {
        say Hi
    }
}

log info Stop