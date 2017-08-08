-- phpMyAdmin SQL Dump
-- version 4.2.12deb2+deb8u1
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Mar 18, 2016 at 01:14 PM
-- Server version: 5.5.47-0+deb8u1
-- PHP Version: 5.6.17-0+deb8u1

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `kicadpartman`
--

-- --------------------------------------------------------

--
-- Table structure for table `bom`
--

CREATE TABLE IF NOT EXISTS `bom` (
`id` int(11) NOT NULL,
  `name` varchar(50) NOT NULL,
  `version` varchar(50) NOT NULL,
  `revision` int(11) NOT NULL,
  `csv` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `categories`
--

CREATE TABLE IF NOT EXISTS `categories` (
`id` int(11) NOT NULL,
  `parent` int(11) DEFAULT NULL,
  `shortname` varchar(20) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `fullname` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `value1` varchar(50) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `value2` varchar(50) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `value3` varchar(50) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `description` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL
) ENGINE=InnoDB AUTO_INCREMENT=67 DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `flow`
--

CREATE TABLE IF NOT EXISTS `flow` (
`id` int(11) NOT NULL,
  `part` int(11) NOT NULL,
  `count` int(11) NOT NULL,
  `bom` int(11) NOT NULL DEFAULT '0',
  `price` float NOT NULL DEFAULT '0',
  `currency` varchar(10) NOT NULL DEFAULT '',
  `description` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB AUTO_INCREMENT=121 DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `mfgs`
--

CREATE TABLE IF NOT EXISTS `mfgs` (
`id` int(11) NOT NULL,
  `shortname` varchar(20) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `fullname` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `www` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `address` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `note` text CHARACTER SET utf8 COLLATE utf8_unicode_ci
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `parts`
--

CREATE TABLE IF NOT EXISTS `parts` (
`id` int(11) NOT NULL,
  `category` int(11) NOT NULL,
  `partname` varchar(50) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `partlabel` varchar(50) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `component` varchar(50) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `footprint` varchar(50) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `value1` float DEFAULT NULL,
  `value2` float DEFAULT NULL,
  `value3` float DEFAULT NULL,
  `rohs` tinyint(1) NOT NULL,
  `smd` tinyint(1) NOT NULL,
  `generic` tinyint(1) NOT NULL,
  `state` tinyint(4) NOT NULL,
  `description` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL
) ENGINE=InnoDB AUTO_INCREMENT=465 DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `spares`
--

CREATE TABLE IF NOT EXISTS `spares` (
`id` int(11) NOT NULL,
  `partid` int(11) NOT NULL,
  `mfg` int(11) NOT NULL,
  `partnumber` varchar(50) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `supplier` int(11) NOT NULL,
  `state` tinyint(4) NOT NULL,
  `description` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL
) ENGINE=InnoDB AUTO_INCREMENT=466 DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `stock`
--

CREATE TABLE IF NOT EXISTS `stock` (
`id` int(11) NOT NULL,
  `count` int(11) NOT NULL,
  `price` float NOT NULL,
  `currency` varchar(10) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL
) ENGINE=InnoDB AUTO_INCREMENT=465 DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `suppliers`
--

CREATE TABLE IF NOT EXISTS `suppliers` (
`id` int(11) NOT NULL,
  `shortname` varchar(50) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `fullname` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `www` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `address` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `note` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `bom`
--
ALTER TABLE `bom`
 ADD PRIMARY KEY (`id`);

--
-- Indexes for table `categories`
--
ALTER TABLE `categories`
 ADD PRIMARY KEY (`id`);

--
-- Indexes for table `flow`
--
ALTER TABLE `flow`
 ADD PRIMARY KEY (`id`);

--
-- Indexes for table `mfgs`
--
ALTER TABLE `mfgs`
 ADD PRIMARY KEY (`id`), ADD KEY `shortname` (`shortname`);

--
-- Indexes for table `parts`
--
ALTER TABLE `parts`
 ADD PRIMARY KEY (`id`);

--
-- Indexes for table `spares`
--
ALTER TABLE `spares`
 ADD PRIMARY KEY (`id`), ADD KEY `partid` (`partid`);

--
-- Indexes for table `stock`
--
ALTER TABLE `stock`
 ADD PRIMARY KEY (`id`);

--
-- Indexes for table `suppliers`
--
ALTER TABLE `suppliers`
 ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `bom`
--
ALTER TABLE `bom`
MODIFY `id` int(11) NOT NULL AUTO_INCREMENT,AUTO_INCREMENT=3;
--
-- AUTO_INCREMENT for table `categories`
--
ALTER TABLE `categories`
MODIFY `id` int(11) NOT NULL AUTO_INCREMENT,AUTO_INCREMENT=67;
--
-- AUTO_INCREMENT for table `flow`
--
ALTER TABLE `flow`
MODIFY `id` int(11) NOT NULL AUTO_INCREMENT,AUTO_INCREMENT=121;
--
-- AUTO_INCREMENT for table `mfgs`
--
ALTER TABLE `mfgs`
MODIFY `id` int(11) NOT NULL AUTO_INCREMENT,AUTO_INCREMENT=15;
--
-- AUTO_INCREMENT for table `parts`
--
ALTER TABLE `parts`
MODIFY `id` int(11) NOT NULL AUTO_INCREMENT,AUTO_INCREMENT=465;
--
-- AUTO_INCREMENT for table `spares`
--
ALTER TABLE `spares`
MODIFY `id` int(11) NOT NULL AUTO_INCREMENT,AUTO_INCREMENT=466;
--
-- AUTO_INCREMENT for table `stock`
--
ALTER TABLE `stock`
MODIFY `id` int(11) NOT NULL AUTO_INCREMENT,AUTO_INCREMENT=465;
--
-- AUTO_INCREMENT for table `suppliers`
--
ALTER TABLE `suppliers`
MODIFY `id` int(11) NOT NULL AUTO_INCREMENT,AUTO_INCREMENT=5;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
