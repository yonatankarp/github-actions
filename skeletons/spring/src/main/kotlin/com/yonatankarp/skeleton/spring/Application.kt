package com.yonatankarp.skeleton.spring

import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.runApplication
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.RestController

@SpringBootApplication
class Application

@RestController
class HelloController {
    @GetMapping("/")
    fun hello() = "Hello from Spring"
}

fun main(args: Array<String>) {
    runApplication<Application>(*args)
}
