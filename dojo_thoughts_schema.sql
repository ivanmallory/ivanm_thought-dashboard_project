-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema dojo_thoughts
-- -----------------------------------------------------
DROP SCHEMA IF EXISTS `dojo_thoughts` ;

-- -----------------------------------------------------
-- Schema dojo_thoughts
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `dojo_thoughts` DEFAULT CHARACTER SET utf8 ;
USE `dojo_thoughts` ;

-- -----------------------------------------------------
-- Table `dojo_thoughts`.`users`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `dojo_thoughts`.`users` ;

CREATE TABLE IF NOT EXISTS `dojo_thoughts`.`users` (
  `id_users` INT NOT NULL AUTO_INCREMENT,
  `first_name` VARCHAR(255) NOT NULL,
  `last_name` VARCHAR(255) NOT NULL,
  `email` VARCHAR(255) NOT NULL,
  `password` VARCHAR(255) NOT NULL,
  `created_at` DATETIME NOT NULL,
  `updated_at` DATETIME NOT NULL,
  PRIMARY KEY (`id_users`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `dojo_thoughts`.`thoughts`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `dojo_thoughts`.`thoughts` ;

CREATE TABLE IF NOT EXISTS `dojo_thoughts`.`thoughts` (
  `id_thoughts` INT NOT NULL AUTO_INCREMENT,
  `content` LONGTEXT NOT NULL,
  `author` INT NOT NULL,
  `created_at` DATETIME NOT NULL,
  `updated_at` DATETIME NOT NULL,
  PRIMARY KEY (`id_thoughts`),
  INDEX `fk_thoughts_users_idx` (`author` ASC) VISIBLE,
  CONSTRAINT `fk_thoughts_users`
    FOREIGN KEY (`author`)
    REFERENCES `dojo_thoughts`.`users` (`id_users`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `dojo_thoughts`.`liked_thoughts`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `dojo_thoughts`.`liked_thoughts` ;

CREATE TABLE IF NOT EXISTS `dojo_thoughts`.`liked_thoughts` (
  `users_id_users` INT NOT NULL,
  `thoughts_id_thoughts` INT NOT NULL,
  PRIMARY KEY (`users_id_users`, `thoughts_id_thoughts`),
  INDEX `fk_users_has_thoughts_thoughts1_idx` (`thoughts_id_thoughts` ASC) VISIBLE,
  INDEX `fk_users_has_thoughts_users1_idx` (`users_id_users` ASC) VISIBLE,
  CONSTRAINT `fk_users_has_thoughts_users1`
    FOREIGN KEY (`users_id_users`)
    REFERENCES `dojo_thoughts`.`users` (`id_users`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_users_has_thoughts_thoughts1`
    FOREIGN KEY (`thoughts_id_thoughts`)
    REFERENCES `dojo_thoughts`.`thoughts` (`id_thoughts`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
