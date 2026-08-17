plugins {
    kotlin("jvm") version "2.4.10"
    id("io.ktor.plugin") version "3.5.2"
}

kotlin {
    jvmToolchain(25)
}

repositories {
    mavenCentral()
}

application {
    mainClass.set("com.yonatankarp.skeleton.ktor.ApplicationKt")
}

ktor {
    fatJar {
        archiveFileName.set("ktor-skeleton.jar")
    }
}

dependencies {
    implementation("io.ktor:ktor-server-core")
    implementation("io.ktor:ktor-server-netty")
    implementation("ch.qos.logback:logback-classic:1.6.3")
    testImplementation("io.ktor:ktor-server-test-host")
    testImplementation(kotlin("test"))
}

tasks.test {
    useJUnitPlatform()
}
