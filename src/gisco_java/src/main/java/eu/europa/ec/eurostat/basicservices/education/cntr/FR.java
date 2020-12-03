package eu.europa.ec.eurostat.basicservices.education.cntr;

import java.io.File;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import org.apache.commons.csv.CSVFormat;

import eu.europa.ec.eurostat.basicservices.BasicServicesUtil;
import eu.europa.ec.eurostat.basicservices.education.EducationUtil;
import eu.europa.ec.eurostat.basicservices.education.Validation;
import eu.europa.ec.eurostat.jgiscotools.gisco_processes.LocalParameters;
import eu.europa.ec.eurostat.jgiscotools.io.CSVUtil;
import eu.europa.ec.eurostat.jgiscotools.io.web.HTTPUtil;

public class FR {

	public static void main(String[] args) {
		System.out.println("Start");
		/*
		#https://www.education.gouv.fr/
			#https://data.education.gouv.fr/
			#https://data.education.gouv.fr/map/

			# Annuaire de l'éducation
			# Annuaire de l'éducation : données sur les établissements publics et privés ouverts situés en France. Le jeu de données couvre le premier degré, le second degré, les Centre d'Information et d'Orientation ainsi que les établissements administratifs.
			# fr-en-annuaire-education
			# 66460

			#https://data.education.gouv.fr/explore/dataset/fr-en-annuaire-education/table/?disjunctive.nom_etablissement&disjunctive.type_etablissement&disjunctive.appartenance_education_prioritaire&disjunctive.type_contrat_prive&disjunctive.code_type_contrat_prive&disjunctive.pial
			#https://data.education.gouv.fr/explore/dataset/fr-en-annuaire-education/download/?format=csv&timezone=Europe/Berlin&lang=fr&use_labels_for_header=true&csv_separator=%3B
		 */

		//download data when FR_raw.csv file is not present
		String url = "https://data.education.gouv.fr/explore/dataset/fr-en-annuaire-education/download/?format=csv&timezone=Europe/Berlin&lang=fr&use_labels_for_header=true&csv_separator=%3B";
		String inFilePath = EducationUtil.path + "FR/FR_raw.csv";
		if(!new File(inFilePath).exists()) {
			System.out.println("Download...");
			LocalParameters.loadProxySettings();
			HTTPUtil.downloadFromURL(url, inFilePath);
		}

		// load data
		CSVFormat csvF = CSVFormat.DEFAULT.withFirstRecordAsHeader().withDelimiter(';');
		List<Map<String, String>> data = CSVUtil.load(inFilePath, csvF);
		System.out.println(data.size());

		//remove unused columns
		CSVUtil.removeColumn(data,
				"date_ouverture",
				"Appartenance_Education_Prioritaire", "GRETA", "SIREN_SIRET",
				"Libelle_departement", "Libelle_academie", "Libelle_region",
				"Fiche_onisep",
				"etat", "ministere_tutelle", "etablissement_multi_lignes",
				"rpi_concentre", "rpi_disperse",
				"Voie_generale","Voie_technologique","Voie_professionnelle",
				"Restauration","Hebergement","ULIS","Apprentissage", "Segpa",
				"Section_arts","Section_cinema","Section_theatre",
				"Section_sport","Section_internationale","Section_europeenne",
				"Lycee_Agricole","Lycee_militaire","Lycee_des_metiers",
				"nom_circonscription",
				"coordonnee_X", "coordonnee_Y", "position", "epsg",
				"Fax",
				"Code_departement", "Code_academie", "Code_region", "Code_commune",
				"Code_type_contrat_prive",
				"PIAL",
				"etablissement_mere", "type_rattachement_etablissement_mere",
				"code_bassin_formation", "libelle_bassin_formation");

		//filter by "Type_etablissement"
		//[Service Administratif, Ecole, Lycée, EREA, Collège, Information et orientation]
		data = data.stream().filter(
				d -> {
					String t = d.get("Type_etablissement");
					return t.equals("Ecole") || t.equals("Lycée") || t.equals("Collège");
				}).collect(Collectors.toList());
		System.out.println(data.size());

		//set levels
		for (Map<String, String> s : data) {
			String mat = s.get("Ecole_maternelle");
			String elem = s.get("Ecole_elementaire");
			String tet = s.get("Type_etablissement");
			String lvls = "";
			if(tet.equals("Lycée") || tet.equals("Collège"))
				lvls = "2";
			else if(mat.contentEquals("0") && elem.contentEquals("1"))
				lvls = "1";
			else if(mat.contentEquals("1") && elem.contentEquals("0"))
				lvls = "0";
			else if(mat.contentEquals("1") && elem.contentEquals("1"))
				lvls = "0-1";
			else {
				System.err.println("Non handled case for education level for FR");
			}

			if(s.get("Post_BAC").equals("1")) lvls += "-3";

			s.put("levels", lvls);
		}
		CSVUtil.removeColumn(data,
				"Post_BAC", "Type_etablissement",
				"Ecole_maternelle", "Ecole_elementaire");


		//TODO
		//"street", "house_number" 
		//Adresse_1;Adresse_2;Adresse_3

		//TODO public_private
		//CSVUtil.getUniqueValues(data, "Statut_public_prive", true);
		//[, Privé, Public, -]
		//;Type_contrat_prive
		//;"code_nature";"libelle_nature;
		//CSVUtil.getUniqueValues(data, "date_maj_ligne", true);
		//CSVUtil.getUniqueValues(data, "precision_localisation", true);

		//set geo_qual - 1: Good, 2: Medium, 3: Low, -1: Unknown.
		for (Map<String, String> s : data) {
			int gq = -1;
			String pl = s.get("precision_localisation");
			switch (pl) {
			case "Rue": gq=1; break;
			case "ZONE_ADRESSAGE": gq=1; break;
			case "CENTROIDE (D'EMPRISE)": gq=1; break;
			case "BATIMENT": gq=1; break;
			case "CENTRE_PARCELLE_PROJETE": gq=1; break;
			case "NUMERO (ADRESSE)": gq=1; break;
			case "Numéro de rue": gq=1; break;
			case "PLAQUE_ADRESSE": gq=1; break;
			case "Lieu-dit": gq=2; break;
			case "COMMUNE": gq=3; break;
			case "Ville": gq=3; break;
			case "": gq=-1; break;
			case "NE SAIT PAS": gq=-1; break;
			default:
				System.err.println("Unhandled geoqual value: " + pl);
				gq=-1;
			}
			s.put("geo_qual", ""+gq);
		}
		CSVUtil.removeColumn(data, "precision_localisation");

		//reference date
		//2020-12-01 to DD/MM/YYYY
		SimpleDateFormat df = new SimpleDateFormat("yyyy-MM-dd");
		for (Map<String, String> s : data) {
			String refDate = s.get("date_maj_ligne");
			try {
				Date rd = df.parse(refDate);
				refDate = BasicServicesUtil.dateFormat.format(rd);
				s.put("date_maj_ligne", refDate);
			} catch (ParseException e) {
				e.printStackTrace();
				s.put("date_maj_ligne", "");
			}
		}
		CSVUtil.renameColumn(data, "date_maj_ligne", "ref_date");

		//rename columns
		CSVUtil.renameColumn(data, "Identifiant_de_l_etablissement", "id");
		CSVUtil.renameColumn(data, "Nom_etablissement", "name");
		CSVUtil.renameColumn(data, "Code postal", "postcode");
		CSVUtil.renameColumn(data, "Nom_commune", "city");
		CSVUtil.renameColumn(data, "Nombre_d_eleves", "enrollment");
		CSVUtil.renameColumn(data, "latitude", "lat");
		CSVUtil.renameColumn(data, "longitude", "lon");
		CSVUtil.renameColumn(data, "Telephone", "tel");
		CSVUtil.renameColumn(data, "Web", "url");
		CSVUtil.renameColumn(data, "Mail", "email");

		//add missing columns
		CSVUtil.addColumn(data, "cc", "FR");
		CSVUtil.addColumn(data, "country", "France");

		CSVUtil.addColumn(data, "max_students", "");
		CSVUtil.addColumn(data, "comments", "");
		CSVUtil.addColumn(data, "site_name", "");
		CSVUtil.addColumn(data, "fields", "");
		CSVUtil.addColumn(data, "facility_type", "");

		//validation
		//Validation.validate(true, data, "FR");

		//save
		System.out.println(data.size());
		CSVUtil.save(data, EducationUtil.path + "FR/FR.csv");
		//GeoData.save(CSVUtil.CSVToFeatures(data, "lon", "lat"), EducationUtil.path + "FR/FR.gpkg", CRSUtil.getWGS_84_CRS());

		System.out.println("End");
	}

}
