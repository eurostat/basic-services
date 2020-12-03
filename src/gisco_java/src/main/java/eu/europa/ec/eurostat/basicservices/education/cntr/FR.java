package eu.europa.ec.eurostat.basicservices.education.cntr;

import java.io.File;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import org.apache.commons.csv.CSVFormat;

import eu.europa.ec.eurostat.basicservices.education.EducationUtil;
import eu.europa.ec.eurostat.jgiscotools.gisco_processes.LocalParameters;
import eu.europa.ec.eurostat.jgiscotools.io.CSVUtil;
import eu.europa.ec.eurostat.jgiscotools.io.geo.CRSUtil;
import eu.europa.ec.eurostat.jgiscotools.io.geo.GeoData;
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

		//Voie_generale;Voie_technologique;Voie_professionnelle;
		//Restauration;Hebergement;ULIS;Apprentissage;Segpa;
		//Section_arts;Section_cinema;Section_theatre;Section_sport;Section_internationale;Section_europeenne;
		//Lycee_Agricole;Lycee_militaire;Lycee_des_metiers;
		//Post_BAC;Appartenance_Education_Prioritaire;GRETA;SIREN_SIRET
		//Fiche_onisep;position
		//;Type_contrat_prive;Libelle_departement;Libelle_academie;Libelle_region;
		//;
		//date_ouverture;
		//date_maj_ligne
		//;etat;ministere_tutelle;etablissement_multi_lignes;
		//"rpi_concentre";"rpi_disperse"
		//;"code_nature";"libelle_nature;

		//"site_name",
		//"levels", "max_students", "",
		//"fields", "facility_type", "public_private",
		//"ref_date"
		//"comments"


		//remove useless columns
		CSVUtil.removeColumn(data, "nom_circonscription", "coordonnee_X", "coordonnee_Y", "position", "epsg", "Fax", "Code_departement", "Code_academie", "Code_region", "Code_commune", "Code_type_contrat_prive", "PIAL", "etablissement_mere", "type_rattachement_etablissement_mere", "code_bassin_formation", "libelle_bassin_formation");

		//filter Type_etablissement
		//[Service Administratif, Ecole, Lycée, EREA, Collège, Information et orientation]
		data = data.stream().filter(
				d -> {
					String t = d.get("Type_etablissement");
					return t.equals("Ecole") || t.equals("Lycée") || t.equals("Collège");
				}).collect(Collectors.toList());
		System.out.println(data.size());

		//levels
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
				System.err.println("aaa");
			}
			s.put("levels", lvls);
		}
		CSVUtil.removeColumn(data, "Ecole_maternelle", "Ecole_elementaire", "Type_etablissement");

		//TODO
		//"street", "house_number" 
		//Adresse_1;Adresse_2;Adresse_3


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

		//TODO
		//"geo_qual",
		//precision_localisation;

		//add columns
		CSVUtil.addColumn(data, "cc", "FR");
		CSVUtil.addColumn(data, "country", "France");

		//CSVUtil.getUniqueValues(data, "Statut_public_prive", true);
		//[, Privé, Public, -]


		//Validation.validate(true, out, "FR");

		//save
		System.out.println(data.size());
		CSVUtil.save(data, EducationUtil.path + "FR/FR.csv");
		GeoData.save(CSVUtil.CSVToFeatures(data, "lon", "lat"), EducationUtil.path + "FR/FR.gpkg", CRSUtil.getWGS_84_CRS());

		System.out.println("End");
	}

}
