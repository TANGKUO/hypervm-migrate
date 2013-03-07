-- phpMyAdmin SQL Dump
-- version 3.4.7
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Mar 07, 2013 at 09:20 PM
-- Server version: 5.5.29
-- PHP Version: 5.3.19

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";

--
-- Database: `transfer`
--

-- --------------------------------------------------------

--
-- Table structure for table `emails`
--

CREATE TABLE IF NOT EXISTS `emails` (
  `Id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `EmailAddress` varchar(250) NOT NULL,
  `Key` varchar(16) NOT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `entries`
--

CREATE TABLE IF NOT EXISTS `entries` (
  `Id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `VpsId` varchar(100) NOT NULL,
  `Username` varchar(100) NOT NULL,
  `EmailAddress` varchar(250) DEFAULT NULL,
  `TargetNode` varchar(160) NOT NULL,
  `Position` int(10) unsigned DEFAULT NULL,
  `Finished` tinyint(3) unsigned NOT NULL,
  `DiskUsage` bigint(20) NOT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `servers`
--

CREATE TABLE IF NOT EXISTS `servers` (
  `Id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `Host` varchar(200) NOT NULL,
  `Busy` tinyint(3) unsigned NOT NULL,
  `Current` int(10) unsigned NOT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;
