plugins {
    kotlin("jvm") version "2.4.0"
    id("io.ktor.plugin") version "3.5.0"
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
    implementation("ch.qos.logback:logback-classic:1.5.37")
    testImplementation("io.ktor:ktor-server-test-host")
    testImplementation(kotlin("test"))
}

tasks.test {
    useJUnitPlatform()
}
